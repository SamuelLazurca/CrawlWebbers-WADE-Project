import logging
import re
from typing import List, Union

from app.core.sparql import run_sparql
from app.models.schemas import FilterRequest, FilterOperator, FilterResultItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _format_value_for_sparql(value: Union[str, int, float]) -> str:
    """
    - Numbers -> 4.5
    - URIs -> <http://...>
    - Dates -> '2023-01-01'^^xsd:dateTime
    - Strings -> 'text'
    """
    if isinstance(value, (int, float)):
        return str(value)

    val_str = str(value)

    if val_str.startswith("http://") or val_str.startswith("https://"):
        return f"<{val_str}>"
    if re.match(r"^\d{4}-\d{2}-\d{2}", val_str):
        return f"'{val_str}'^^xsd:dateTime"

    clean_val = val_str.replace("'", "\\'")
    return f"'{clean_val}'"


def build_intelligent_query(request: FilterRequest) -> List[FilterResultItem]:
    select_vars = ["DISTINCT ?s", "?label", "?sType"]
    where_clauses = [f"?s a <{request.dataset_class}> ."]
    filter_clauses = []

    for idx, f in enumerate(request.filters):
        var_name = f"?v{idx}"

        if f.property_uri.startswith("^"):
            prop = f"^<{f.property_uri[1:]}>"
        else:
            prop = f"<{f.property_uri}>"

        select_vars.append(var_name)

        # Graph traversal
        if f.path_to_target:
            intermediate_var = f"?inter_{idx}"
            where_clauses.append(f"?s {prop} {intermediate_var} .")
            where_clauses.append(f"{intermediate_var} <{f.path_to_target}> {var_name} .")
        else:
            where_clauses.append(f"?s {prop} {var_name} .")

        formatted_val = _format_value_for_sparql(f.value)
        val_clean = str(f.value).replace('"', '\\"')

        if f.operator == FilterOperator.TRANSITIVE:
            where_clauses.pop()
            if f.path_to_target: where_clauses.pop()

            target_node = f"<{val_clean}>" if "http" in str(f.value) else f"'{val_clean}'"

            where_clauses.append(f"""
                ?s {prop} ?concept .
                ?concept (skos:broader*|rdfs:subClassOf*) {target_node} .
                BIND({target_node} AS {var_name}) 
            """)

        elif f.operator == FilterOperator.CONTAINS:
            filter_clauses.append(f"FILTER(regex(str({var_name}), \"{val_clean}\", \"i\"))")

        elif f.operator == FilterOperator.NOT_CONTAINS:
            filter_clauses.append(f"FILTER(!regex(str({var_name}), \"{val_clean}\", \"i\"))")

        elif f.operator == FilterOperator.EQUALS:
            filter_clauses.append(f"FILTER({var_name} = {formatted_val})")

        elif f.operator == FilterOperator.NOT_EQUALS:
            filter_clauses.append(f"FILTER({var_name} != {formatted_val})")

        elif f.operator == FilterOperator.GT:
            filter_clauses.append(f"FILTER({var_name} > {formatted_val})")

        elif f.operator == FilterOperator.LT:
            filter_clauses.append(f"FILTER({var_name} < {formatted_val})")

    where_clauses.append("OPTIONAL { ?s rdfs:label ?label }")
    where_clauses.append("OPTIONAL { ?s schema:name ?label }")
    where_clauses.append("OPTIONAL { ?s a ?sType }")

    query_body = "\n".join(where_clauses + filter_clauses)

    query = f"""
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX davi-nist: <http://davi.app/vocab/nist#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT {" ".join(select_vars)}
    WHERE {{
        {query_body}
    }}
    LIMIT {request.limit}
    OFFSET {request.offset}
    """

    logger.info(f"Generated SPARQL:\n{query}")
    results = run_sparql(query)

    items = []
    for r in results:
        uri = r["s"]["value"]

        matches_data = {}
        for idx in range(len(request.filters)):
            v_key = f"v{idx}"
            if v_key in r:
                matches_data[request.filters[idx].property_uri] = r[v_key]["value"]

        if "label" in r:
            label = r["label"]["value"]
        elif "#" in uri:
            label = uri.split("#")[-1]
        else:
            label = uri.split("/")[-1]

        items.append(FilterResultItem(
            uri=uri,
            label=label,
            type=r.get("sType", {}).get("value"),
            matches=matches_data
        ))

    return items
