import os
import json
import shutil
import logging
from urllib.parse import quote

import py7zr
from rdflib import Graph, Literal, RDF, Namespace, URIRef
from rdflib.namespace import RDFS, DCTERMS, OWL, XSD

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cpe-to-rdf")

# Namespaces

CPE_NS    = Namespace("https://nvd.nist.gov/products/cpe/detail/")
VENDOR_NS = Namespace("https://nvd.nist.gov/products/cpe/search/results?keyword=")
VULN      = Namespace("http://example.org/ontology/vulnerability#")

def safe_uri(namespace, value):
    value = value.strip()
    return URIRef(namespace + quote(value, safe=""))

def make_cpe_uri(cpe_id):
    return safe_uri(CPE_NS, cpe_id)

def make_vendor_uri(vendor):
    return safe_uri(VENDOR_NS, vendor.lower())

def add_literal_if_present(g, s, p, value, datatype=None, lang=None):
    if value is None:
        return
    if isinstance(value, str) and not value.strip():
        return
    g.add((s, p, Literal(value, datatype=datatype, lang=lang)))

def init_graph():
    g = Graph()
    g.bind("cpe", CPE_NS)
    g.bind("vendor", VENDOR_NS)
    g.bind("vuln", VULN)
    g.bind("rdfs", RDFS)
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)
    return g

def flush_batch(graph, batch_idx, output_dir):
    path = os.path.join(output_dir, f"cpe_batch_{batch_idx:04d}.ttl")
    log.info("Writing batch %d → %s (%d triples)",
             batch_idx, path, len(graph))
    graph.serialize(path, format="turtle")

def map_cpe_to_rdf(data, part, g):
    cpe_name = data.get("cpeName")
    cpe_id   = data.get("cpeNameId")

    if not cpe_name or not cpe_id:
        return

    product_uri = make_cpe_uri(cpe_id)

    g.add((product_uri, RDF.type, VULN.Product))
    g.add((product_uri, DCTERMS.identifier, Literal(cpe_name)))

    parts = cpe_name.split(":")
    if len(parts) < 6:
        return

    vendor_name  = parts[3]
    product_name = parts[4]
    version      = parts[5]

    vendor_uri = make_vendor_uri(vendor_name)

    g.add((vendor_uri, RDF.type, VULN.Vendor))
    g.add((vendor_uri, RDFS.label, Literal(vendor_name)))

    add_literal_if_present(g, product_uri, VULN.productName, product_name)
    add_literal_if_present(g, product_uri, VULN.productVersion, version)
    g.add((product_uri, VULN.vendor, vendor_uri))

    if part == "a":
        g.add((product_uri, RDF.type, VULN.SoftwareApplication))
    elif part == "o":
        g.add((product_uri, RDF.type, VULN.OperatingSystem))
    elif part == "h":
        g.add((product_uri, RDF.type, VULN.HardwareDevice))

    for title in data.get("titles", []):
        if title.get("lang") == "en":
            g.add((product_uri, RDFS.label,
                   Literal(title.get("title"), lang="en")))
            break

def process_cpe_json_folders(root_folder, output_dir, batch_size=2000):
    os.makedirs(output_dir, exist_ok=True)

    temp_dir = "_tmp_extract"
    os.makedirs(temp_dir, exist_ok=True)

    g = init_graph()
    batch_idx = 0
    item_count = 0

    # application, hardware, OS
    for part in ("a", "h", "o"):
        part_dir = os.path.join(root_folder, part)
        if not os.path.isdir(part_dir):
            continue

        log.info("Processing CPE category: %s", part)

        for fname in sorted(os.listdir(part_dir)):
            if not fname.endswith(".7z"):
                continue

            archive_path = os.path.join(part_dir, fname)

            with py7zr.SevenZipFile(archive_path, "r") as z:
                z.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for f in files:
                    if not f.endswith(".json"):
                        continue

                    with open(os.path.join(root, f), encoding="utf-8") as fh:
                        map_cpe_to_rdf(json.load(fh), part, g)

                    item_count += 1

                    if item_count % batch_size == 0:
                        flush_batch(g, batch_idx, output_dir)
                        batch_idx += 1
                        g = init_graph()

            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)

    if len(g):
        flush_batch(g, batch_idx, output_dir)

    shutil.rmtree(temp_dir)
    log.info("All CPE batches generated")

# Run

if __name__ == "__main__":
    process_cpe_json_folders(
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/NIST_NVD/CPE",
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/results/cpe_rdf_batches"
    )
