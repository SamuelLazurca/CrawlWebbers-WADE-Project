import os
import json
import re
import shutil
import logging
from urllib.parse import quote

import py7zr
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD, RDFS, DCTERMS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cve-to-rdf")

# Namespaces

CVE  = Namespace("https://nvd.nist.gov/vuln/detail/")
CWE  = Namespace("https://cwe.mitre.org/data/definitions/")
CPE  = Namespace("https://nvd.nist.gov/products/cpe/detail/")
CVSS = Namespace("https://www.first.org/cvss/")
VULN = Namespace("http://example.org/ontology/vulnerability#")

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
    g.bind("cvss", CVSS)
    g.bind("vuln", VULN)
    g.bind("dcterms", DCTERMS)
    return g

def parse_cve_json(data, g):
    cve_id = data.get("id")
    if not cve_id:
        return

    cve_uri = CVE[cve_id]

    g.add((cve_uri, RDF.type, VULN.Vulnerability))
    g.add((cve_uri, RDFS.label, Literal(cve_id)))
    g.add((cve_uri, DCTERMS.identifier, Literal(cve_id)))

    add_literal_if_present(
        g, cve_uri, VULN.vulnerabilityStatus, data.get("vulnStatus")
    )
    add_literal_if_present(
        g, cve_uri, DCTERMS.source, data.get("sourceIdentifier")
    )

    for d in data.get("descriptions", []):
        if d.get("lang") == "en":
            add_literal_if_present(
                g, cve_uri, DCTERMS.description, d.get("value"), lang="en"
            )

    add_literal_if_present(
        g, cve_uri, DCTERMS.issued,
        data.get("published"), datatype=XSD.dateTime
    )
    add_literal_if_present(
        g, cve_uri, DCTERMS.modified,
        data.get("lastModified"), datatype=XSD.dateTime
    )

    for weakness in data.get("weaknesses", []):
        for desc in weakness.get("description", []):
            m = re.search(r"CWE-(\d+)", desc.get("value", ""))
            if m:
                g.add((cve_uri, VULN.hasWeakness, CWE[m.group(1)]))

    # CPE
    for cfg in data.get("configurations", []):
        for node in cfg.get("nodes", []):
            for match in node.get("cpeMatch", []):
                cpe_id = match.get("matchCriteriaId")
                if cpe_id:
                    g.add((cve_uri, VULN.affectsProduct, make_cpe_uri(cpe_id)))

    for ref in data.get("references", []):
        url = ref.get("url")
        if url:
            g.add((cve_uri, VULN.referenceURL, URIRef(url)))

    # CVSS
    parse_cvss_metrics(data.get("metrics", {}), cve_uri, g)

def parse_cvss_metrics(metrics, cve_uri, g):
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        for entry in metrics.get(key, []):
            if entry.get("type") != "Primary":
                continue

            cvss = entry.get("cvssData", {})
            version = cvss.get("version")
            if not version:
                continue

            metric_uri = URIRef(f"{cve_uri}/cvss/{version}")

            g.add((metric_uri, RDF.type, VULN.CVSSMetric))
            g.add((cve_uri, VULN.hasCVSSMetric, metric_uri))

            add_literal_if_present(
                g, metric_uri, VULN.baseScore,
                cvss.get("baseScore"), datatype=XSD.float
            )
            add_literal_if_present(
                g, metric_uri, VULN.vectorString,
                cvss.get("vectorString")
            )
            add_literal_if_present(
                g, metric_uri, VULN.exploitabilityScore,
                entry.get("exploitabilityScore"), datatype=XSD.float
            )
            add_literal_if_present(
                g, metric_uri, VULN.impactScore,
                entry.get("impactScore"), datatype=XSD.float
            )

def process_all_cves(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = "_tmp_extract"
    os.makedirs(temp_dir, exist_ok=True)

    batch_idx = 0

    for fname in sorted(os.listdir(input_dir)):
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
                            parse_cve_json(json.load(fh), g)

        finally:
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)

        out = os.path.join(output_dir, f"cve_batch_{batch_idx:04d}.ttl")
        log.info("Writing %s (%d triples)", out, len(g))
        g.serialize(out, format="turtle")
        g.remove((None, None, None))

        batch_idx += 1

    shutil.rmtree(temp_dir)
    log.info("All CVE batches generated ✔")

# Run

if __name__ == "__main__":
    process_all_cves(
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/NIST_NVD/CVE",
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/results/cve_rdf_batches"
    )
