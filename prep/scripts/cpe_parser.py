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

# --- NAMESPACES ---
CPE_NS = Namespace("https://nvd.nist.gov/products/cpe/detail/")
VENDOR_NS = Namespace("https://nvd.nist.gov/products/cpe/search/results?keyword=")
DAVI_NIST = Namespace("http://davi.app/vocab/nist#")
SCHEMA = Namespace("http://schema.org/")


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
    g.bind("davi-nist", DAVI_NIST)
    g.namespace_manager.bind("schema", "http://schema.org/", override=True, replace=True)
    g.bind("dcterms", DCTERMS)
    return g


def flush_batch(graph, batch_idx, output_dir):
    path = os.path.join(output_dir, f"cpe_batch_{batch_idx:04d}.ttl")
    log.info("Writing batch %d → %s (%d triples)",
             batch_idx, path, len(graph))
    graph.serialize(path, format="turtle")


def map_cpe_to_rdf(data, part, g):
    cpe_name = data.get("cpeName")
    cpe_id = data.get("cpeNameId")

    if not cpe_name or not cpe_id:
        return

    product_uri = make_cpe_uri(cpe_id)

    # 1. Identifier
    g.add((product_uri, DCTERMS.identifier, Literal(cpe_name)))

    parts = cpe_name.split(":")
    if len(parts) < 6:
        return

    vendor_name = parts[3]
    product_name = parts[4]
    version = parts[5]

    # 2. Vendor -> schema:Organization
    vendor_uri = make_vendor_uri(vendor_name)
    g.add((vendor_uri, RDF.type, SCHEMA.Organization))
    g.add((vendor_uri, SCHEMA.name, Literal(vendor_name)))

    # 3. Product Properties -> schema:name, schema:softwareVersion, schema:manufacturer
    # Note: We use schema:name for the product name to be compatible with your SPA
    add_literal_if_present(g, product_uri, SCHEMA.name, product_name)
    add_literal_if_present(g, product_uri, SCHEMA.softwareVersion, version)
    g.add((product_uri, SCHEMA.manufacturer, vendor_uri))

    # 4. Product Type Mapping
    # 'a' = Application, 'o' = OS -> schema:SoftwareApplication
    # 'h' = Hardware -> schema:Product (Hardware isn't strictly software, but is a product)
    if part in ["a", "o"]:
        g.add((product_uri, RDF.type, SCHEMA.SoftwareApplication))
    elif part == "h":
        g.add((product_uri, RDF.type, SCHEMA.Product))

    # 5. Titles (Multilingual labels)
    for title in data.get("titles", []):
        if title.get("lang") == "en":
            g.add((product_uri, RDFS.label, Literal(title.get("title"), lang="en")))
            break


def process_cpe_json_folders(root_folder, output_dir, batch_size=2000):
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = "_tmp_extract_cpe"
    os.makedirs(temp_dir, exist_ok=True)

    g = init_graph()
    batch_idx = 0
    item_count = 0

    for part in ("a", "h", "o"):
        part_dir = os.path.join(root_folder, part)
        if not os.path.isdir(part_dir):
            continue

        log.info("Processing CPE category: %s", part)

        for fname in sorted(os.listdir(part_dir)):
            if not fname.endswith(".7z"):
                continue

            archive_path = os.path.join(part_dir, fname)
            try:
                with py7zr.SevenZipFile(archive_path, "r") as z:
                    z.extractall(temp_dir)
            except Exception as e:
                log.error(f"Failed to extract {archive_path}: {e}")
                continue

            for root, _, files in os.walk(temp_dir):
                for f in files:
                    if not f.endswith(".json"):
                        continue

                    try:
                        with open(os.path.join(root, f), encoding="utf-8") as fh:
                            map_cpe_to_rdf(json.load(fh), part, g)
                    except Exception as e:
                        log.warning(f"Error parsing JSON {f}: {e}")
                        continue

                    item_count += 1
                    if item_count % batch_size == 0:
                        flush_batch(g, batch_idx, output_dir)
                        batch_idx += 1
                        g = init_graph()

            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)

    if len(g):
        flush_batch(g, batch_idx, output_dir)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    log.info("All CPE batches generated")


if __name__ == "__main__":
    process_cpe_json_folders(
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/NIST_NVD/CPE",
        "D:/Master/Anul2Sem1/WADE/Project/davi/data/results/cpe_rdf_batches"
    )
