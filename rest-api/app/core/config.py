import os

# Allow environment variable override for Docker/Cloud deployment
FUSEKI_ENDPOINT = os.getenv("SPARQL_ENDPOINT", "http://localhost:3030/davi/sparql")

PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>

# DaVi Custom Namespaces
PREFIX davi-meta: <http://davi.app/vocab/meta#>
PREFIX davi-nist: <http://davi.app/vocab/nist#>
PREFIX davi-mov: <http://davi.app/vocab/movielens#>
"""
