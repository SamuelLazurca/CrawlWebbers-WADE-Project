import os
import json
import re
import shutil
import logging
from urllib.parse import quote

import py7zr
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD, DCTERMS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cve-to-rdf")

# NAMESPACES
CVE = Namespace("https://nvd.nist.gov/vuln/detail/")
CWE = Namespace("https://cwe.mitre.org/data/definitions/")
CPE = Namespace("https://nvd.nist.gov/products/cpe/detail/")
CVSS_STD = Namespace("https://www.first.org/cvss/")
DAVI_NIST = Namespace("https://purl.org/davi/vocab/nist#")
SCHEMA = Namespace("http://schema.org/")

CPE_MAP_PATH = "D:/Master/Anul2Sem1/WADE/Project/davi/data/results/cpe_map.json"


def safe_uri(namespace, value):
    value = value.strip()
    return URIRef(namespace + quote(value, safe=""))


def make_cpe_uri(cpe_id):
    return safe_uri(CPE, cpe_id)


def add_literal_if_present(g, s, p, value, datatype=None, lang=None):
    if value is None:
        return
    if isinstance(value, str) and not value.strip():
        return
    g.add((s, p, Literal(value, datatype=datatype, lang=lang)))


def init_graph():
    g = Graph()
    g.bind("cve", CVE)
    g.bind("cwe", CWE)
    g.bind("cpe", CPE)
    g.bind("davi-nist", DAVI_NIST)
    g.namespace_manager.bind("schema", "http://schema.org/", override=True, replace=True)
    g.bind("dcterms", DCTERMS)
    return g


def parse_cve_json(data, g, cpe_map):
    cve_id = data.get("id")
    if not cve_id:
        return

    cve_uri = CVE[cve_id]

    g.add((cve_uri, RDF.type, DAVI_NIST.Vulnerability))
    g.add((cve_uri, SCHEMA.name, Literal(cve_id))) 
    g.add((cve_uri, DCTERMS.identifier, Literal(cve_id)))

    for d in data.get("descriptions", []):
        if d.get("lang") == "en":
            add_literal_if_present(
                g, cve_uri, SCHEMA.description, d.get("value"), lang="en"
            )

    add_literal_if_present(
        g, cve_uri, SCHEMA.datePublished,
        data.get("published"), datatype=XSD.dateTime
    )
    add_literal_if_present(
        g, cve_uri, SCHEMA.dateModified,
        data.get("lastModified"), datatype=XSD.dateTime
    )

    add_literal_if_present(
        g, cve_uri, SCHEMA.creativeWorkStatus, data.get("vulnStatus")
    )

    # WEAKNESSES
    for weakness in data.get("weaknesses", []):
        for desc in weakness.get("description", []):
            m = re.search(r"CWE-(\d+)", desc.get("value", ""))
            if m:
                g.add((cve_uri, DAVI_NIST.hasWeakness, CWE[m.group(1)]))

    # AFFECTED PRODUCTS
    for cfg in data.get("configurations", []):
        for node in cfg.get("nodes", []):
            for match in node.get("cpeMatch", []):
                criteria = match.get("criteria") or match.get("cpe23Uri") or match.get("cpe")
                match_id = match.get("matchCriteriaId")
                if not criteria and not match_id:
                    continue

                cpe_id = cpe_map.get(criteria)
                if cpe_id:
                    product_uri = make_cpe_uri(cpe_id)  # CPE_NS + UUID (existing resource)
                    g.add((cve_uri, DAVI_NIST.affectsSoftware, product_uri))

    for ref in data.get("references", []):
        url = ref.get("url")
        if url:
            g.add((cve_uri, SCHEMA.url, URIRef(url)))

    # Pass the cve_uri to metric parser so we can mint a unique sub-URI
    parse_cvss_metrics(data.get("metrics", {}), cve_uri, g)


def parse_cvss_metrics(metrics, cve_uri, g):
    """
    Creates a distinct metric node (Reification).
    URI Style: davi-nist:metric_CVE-ID_vVERSION
    """
    # Extract the CVE ID string from the URI (e.g., "CVE-1999-0199")
    cve_id_str = cve_uri.split("/")[-1]

    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        for entry in metrics.get(key, []):
            if entry.get("type") != "Primary":
                continue

            cvss = entry.get("cvssData", {})
            version = cvss.get("version")
            if not version:
                continue

            if version == "2.0" or version == "1.0":
                version = version[0]  # Simplify to "2" or "1"

            ver_clean = version.replace(".", "-")

            metric_node_name = f"metric_{cve_id_str}_v{ver_clean}"
            metric_uri = DAVI_NIST[metric_node_name]

            g.add((cve_uri, DAVI_NIST.hasCVSSMetric, metric_uri))

            g.add((metric_uri, RDF.type, DAVI_NIST.CVSSMetric))

            std_ver = version[0] if version.startswith(("1", "2")) else version
            g.add((metric_uri, DCTERMS.conformsTo, URIRef(f"https://www.first.org/cvss/v{std_ver}")))

            add_literal_if_present(
                g, metric_uri, DAVI_NIST.baseScore,
                cvss.get("baseScore"), datatype=XSD.decimal
            )
            add_literal_if_present(
                g, metric_uri, DAVI_NIST.vectorString,
                cvss.get("vectorString")
            )


def process_all_cves(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = "_tmp_extract_cve"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with open(CPE_MAP_PATH, "r", encoding="utf-8") as mf:
            cpe_map = json.load(mf)
        log.info("Loaded CPE mapping (%d entries) from %s", len(cpe_map), CPE_MAP_PATH)
    except Exception as e:
        log.error("Could not load CPE map: %s", e)
        cpe_map = {}

    batch_idx = 0

    for fname in sorted(os.listdir(input_dir))[:10]:
        if not fname.endswith(".7z"):
            continue

        archive = os.path.join(input_dir, fname)
        log.info("Processing %s", fname)

        g = init_graph()

        try:
            with py7zr.SevenZipFile(archive, "r") as z:
                z.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for f in files:
                    if f.endswith(".json"):
                        with open(os.path.join(root, f), encoding="utf-8") as fh:
                            parse_cve_json(json.load(fh), g, cpe_map)

        except Exception as e:
            log.error(f"Error processing {fname}: {e}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)

        out = os.path.join(output_dir, f"cve_batch_{batch_idx:04d}.ttl")
        log.info("Writing %s (%d triples)", out, len(g))
        g.serialize(out, format="turtle")

        batch_idx += 1

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    log.info("All CVE batches generated ✔")


if __name__ == "__main__":
    process_all_cves(
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/NIST_NVD/CVE",
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/results/cve_rdf_batches"
    )
