from SPARQLWrapper import SPARQLWrapper, JSON
from app.core.config import FUSEKI_ENDPOINT, PREFIXES

def run_sparql(query: str):
    sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
    sparql.setQuery(PREFIXES + query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()["results"]["bindings"]
