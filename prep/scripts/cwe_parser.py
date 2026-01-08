import zipfile
import xml.etree.ElementTree as ET
import logging
from urllib.parse import quote

from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import SKOS, RDFS, DCTERMS, XSD

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cwe-to-rdf")

# Namespaces

VULN  = Namespace("http://example.org/ontology/vulnerability#")
CWE   = Namespace("https://cwe.mitre.org/data/definitions/")
CAPEC = Namespace("https://capec.mitre.org/data/definitions/")

def detect_xml_namespace(root):
    """Detect XML namespace URI from root tag"""
    if root.tag.startswith("{"):
        return root.tag.split("}")[0].strip("{")
    raise RuntimeError("Could not detect XML namespace")

def safe_uri(namespace, value):
    """Create safe URI fragment"""
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
    g.bind("vuln", VULN)
    g.bind("capec", CAPEC)
    return g

def process_weakness(weakness, ns, g):
    cwe_id = weakness.get("ID")
    name = weakness.get("Name")

    if not cwe_id:
        return

    cwe_uri = CWE[cwe_id]

    # g.add((cwe_uri, RDF.type, VULN.Weakness))
    g.add((cwe_uri, RDF.type, SKOS.Concept))
    g.add((cwe_uri, DCTERMS.identifier, Literal(f"CWE-{cwe_id}")))

    if name:
        g.add((cwe_uri, SKOS.prefLabel,
               Literal(f"CWE-{cwe_id}: {name}", lang="en")))

    for attr in ("Abstraction", "Structure", "Status"):
        value = weakness.get(attr)
        if value:
            concept_uri = safe_uri(VULN, f"{attr}/{value}")
            g.add((concept_uri, RDF.type, SKOS.Concept))
            g.add((concept_uri, SKOS.prefLabel, Literal(value)))
            g.add((cwe_uri, VULN[attr.lower()], concept_uri))

    desc = weakness.findtext("cwe:Description", namespaces=ns)
    add_en_literal(g, cwe_uri, DCTERMS.description, desc)

    loe = weakness.findtext("cwe:Likelihood_Of_Exploit", namespaces=ns)
    if loe:
        loe_uri = safe_uri(VULN, f"Likelihood/{loe}")
        g.add((loe_uri, RDF.type, SKOS.Concept))
        g.add((loe_uri, SKOS.prefLabel, Literal(loe)))
        g.add((cwe_uri, VULN.likelihoodOfExploit, loe_uri))

    # CWE hierarchy
    for rel in weakness.findall(".//cwe:Related_Weakness", ns):
        if rel.get("Nature") == "ChildOf":
            parent_id = rel.get("CWE_ID")
            if parent_id:
                parent_uri = CWE[parent_id]
                g.add((cwe_uri, SKOS.broader, parent_uri))
                g.add((parent_uri, SKOS.narrower, cwe_uri))

    for alt in weakness.findall(".//cwe:Alternate_Term", ns):
        term = alt.findtext("cwe:Term", namespaces=ns)
        desc = alt.findtext("cwe:Description", namespaces=ns)
        add_en_literal(g, cwe_uri, SKOS.altLabel, term)
        add_en_literal(g, cwe_uri, VULN.alternateTermDescription, desc)

    for lang in weakness.findall(".//cwe:Language", ns):
        cls = lang.get("Class")
        if cls:
            uri = safe_uri(VULN, f"language/{cls}")
            g.add((uri, RDF.type, VULN.ProgrammingLanguage))
            g.add((uri, RDFS.label, Literal(cls)))
            g.add((cwe_uri, VULN.appliesToLanguage, uri))

    for tech in weakness.findall(".//cwe:Technology", ns):
        cls = tech.get("Class")
        if cls:
            uri = safe_uri(VULN, f"technology/{cls}")
            g.add((uri, RDF.type, VULN.Technology))
            g.add((uri, RDFS.label, Literal(cls)))
            g.add((cwe_uri, VULN.appliesToTechnology, uri))

    for cons in weakness.findall(".//cwe:Consequence", ns):
        impact = cons.findtext("cwe:Impact", namespaces=ns)
        scope = cons.findtext("cwe:Scope", namespaces=ns)

        if impact:
            cons_uri = safe_uri(VULN, f"consequence/{cwe_id}/{impact}")
            g.add((cons_uri, RDF.type, VULN.Consequence))
            g.add((cons_uri, VULN.impact, Literal(impact)))
            if scope:
                g.add((cons_uri, VULN.scope, Literal(scope)))
            g.add((cwe_uri, VULN.hasConsequence, cons_uri))

    for dm in weakness.findall(".//cwe:Detection_Method", ns):
        dm_id = dm.get("Detection_Method_ID")
        if not dm_id:
            continue

        dm_uri = VULN[f"detection-method/{dm_id}"]

        if (dm_uri, RDF.type, None) not in g:
            g.add((dm_uri, RDF.type, VULN.DetectionMethod))

        method = dm.findtext("cwe:Method", namespaces=ns)
        desc = dm.findtext("cwe:Description", namespaces=ns)
        eff = dm.findtext("cwe:Effectiveness", namespaces=ns)

        if method:
            g.add((dm_uri, RDFS.label, Literal(method)))
        add_en_literal(g, dm_uri, DCTERMS.description, desc)
        if eff:
            g.add((dm_uri, VULN.effectiveness, Literal(eff)))

        g.add((cwe_uri, VULN.detectedBy, dm_uri))

    # CAPEC 
    for capec in weakness.findall(".//cwe:Related_Attack_Pattern", ns):
        capec_id = capec.get("CAPEC_ID")
        if capec_id:
            g.add((cwe_uri, SKOS.related, CAPEC[capec_id]))

# Main

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

    log.info("Detected XML namespace: %s", ns_uri)
    log.info("Processing CWE weaknesses...")

    for weakness in root.findall(".//cwe:Weakness", ns):
        process_weakness(weakness, ns, g)

    log.info("Serializing RDF → %s", output_ttl)
    g.serialize(output_ttl, format="turtle")
    log.info("Done processing CWE XML")

# Run

if __name__ == "__main__":
    zip_loc = r"D:/Master/Anul2Sem1/WADE/Project/davi/data/NIST_NVD/CWE/Full-Downloads/cwec_latest.xml.zip"
    out_ttl = r"D:/Master/Anul2Sem1/WADE/Project/davi/data/results/cwe_rdf.ttl"
    process_cwe_xml(zip_loc, out_ttl)
