import zipfile
import xml.etree.ElementTree as ET
import logging
from urllib.parse import quote

from rdflib import Graph, Literal, RDF, Namespace
from rdflib.namespace import SKOS, DCTERMS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cwe-to-rdf")

# --- NAMESPACES ---
DAVI_NIST = Namespace("http://davi.app/vocab/nist#")
CWE = Namespace("https://cwe.mitre.org/data/definitions/")
CAPEC = Namespace("https://capec.mitre.org/data/definitions/")
SCHEMA = Namespace("http://schema.org/")


def detect_xml_namespace(root):
    if root.tag.startswith("{"):
        return root.tag.split("}")[0].strip("{")
    raise RuntimeError("Could not detect XML namespace")


def safe_uri(namespace, value):
    value = value.strip().replace(" ", "_")
    return namespace[quote(value)]


def add_en_literal(graph, subj, pred, text):
    if text and text.strip():
        graph.add((subj, pred, Literal(text.strip(), lang="en")))


def init_graph():
    g = Graph()
    g.bind("cwe", CWE)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("davi-nist", DAVI_NIST)
    g.namespace_manager.bind("schema", "http://schema.org/", override=True, replace=True)
    g.bind("capec", CAPEC)
    return g


def process_weakness(weakness, ns, g):
    cwe_id = weakness.get("ID")
    name = weakness.get("Name")

    if not cwe_id:
        return

    cwe_uri = CWE[cwe_id]

    # 1. Type: davi-nist:Weakness (subclass of skos:Concept)
    g.add((cwe_uri, RDF.type, DAVI_NIST.Weakness))
    g.add((cwe_uri, RDF.type, SKOS.Concept))

    g.add((cwe_uri, DCTERMS.identifier, Literal(f"CWE-{cwe_id}")))

    if name:
        g.add((cwe_uri, SKOS.prefLabel, Literal(f"CWE-{cwe_id}: {name}", lang="en")))

    # 2. Description -> schema:description
    desc = weakness.findtext("cwe:Description", namespaces=ns)
    add_en_literal(g, cwe_uri, SCHEMA.description, desc)

    # 3. Hierarchy (Parents/Children) -> SKOS
    for rel in weakness.findall(".//cwe:Related_Weakness", ns):
        if rel.get("Nature") == "ChildOf":
            parent_id = rel.get("CWE_ID")
            if parent_id:
                parent_uri = CWE[parent_id]
                g.add((cwe_uri, SKOS.broader, parent_uri))
                g.add((parent_uri, SKOS.narrower, cwe_uri))

    # 4. CAPEC Relations -> SKOS
    for capec in weakness.findall(".//cwe:Related_Attack_Pattern", ns):
        capec_id = capec.get("CAPEC_ID")
        if capec_id:
            g.add((cwe_uri, SKOS.related, CAPEC[capec_id]))

    # 5. Alternate Terms -> SKOS altLabel
    for alt in weakness.findall(".//cwe:Alternate_Term", ns):
        term = alt.findtext("cwe:Term", namespaces=ns)
        add_en_literal(g, cwe_uri, SKOS.altLabel, term)


def process_cwe_xml(zip_path, output_ttl):
    log.info("Opening archive %s", zip_path)
    g = init_graph()

    with zipfile.ZipFile(zip_path, "r") as z:
        xml_file = next(n for n in z.namelist() if n.endswith(".xml"))
        with z.open(xml_file) as f:
            tree = ET.parse(f)
            root = tree.getroot()

    ns_uri = detect_xml_namespace(root)
    ns = {"cwe": ns_uri}

    log.info("Processing CWE weaknesses...")

    for weakness in root.findall(".//cwe:Weakness", ns):
        process_weakness(weakness, ns, g)

    log.info("Serializing RDF → %s", output_ttl)
    g.serialize(output_ttl, format="turtle")
    log.info("Done.")


if __name__ == "__main__":
    zip_loc = r"CWE/Full-Downloads/cwec_latest.xml.zip"
    out_ttl = r"nist/cwe_rdf.ttl"
    process_cwe_xml(zip_loc, out_ttl)
