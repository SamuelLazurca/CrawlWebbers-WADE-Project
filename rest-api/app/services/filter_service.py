import logging
import re
from typing import List, Union

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import FilterRequest, FilterOperator, FilterResultItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_safe_uri(uri: str) -> bool:
    """
    Basic security check to prevent SPARQL injection via property paths.
    Disallows spaces, semi-colons, and brackets which could break out of the query structure.
    """
    unsafe_chars = [" ", ";", "{", "}", "\\", '"', "'"]
    if any(char in uri for char in unsafe_chars):
        return False
    return True


def _format_value_for_sparql(value: Union[str, int, float, bool]) -> str:
    """
    Formats Python values into SPARQL literals.
    - True/False -> 'true'^^xsd:boolean
    - Numbers -> 4.5
    - URIs -> <http://...>
    - Dates -> '2023-01-01'^^xsd:dateTime
    - Strings -> 'text'
    """
    if isinstance(value, bool):
        return f"'{str(value).lower()}'^^xsd:boolean"

    if isinstance(value, (int, float)):
        return str(value)

    val_str = str(value)

    # If it looks like a full URI, wrap it in angle brackets
    if val_str.startswith("http://") or val_str.startswith("https://"):
        return f"<{val_str}>"

    # ISO Date detection (Simple YYYY-MM-DD check)
    if re.match(r"^\d{4}-\d{2}-\d{2}", val_str):
        return f"'{val_str}'^^xsd:dateTime"

    # Default to string literal, escaping quotes
    clean_val = val_str.replace("'", "\\'")
    return f"'{clean_val}'"


def build_intelligent_query(request: FilterRequest) -> List[FilterResultItem]:
    select_vars = ["DISTINCT ?s", "?label", "?sType"]

    # Ensure the dataset class is a safe URI
    if not _is_safe_uri(request.dataset_class):
        raise HTTPException(status_code=400, detail="Invalid Dataset Class URI")

    where_clauses = [f"?s a <{request.dataset_class}> ."]
    filter_clauses = []

    for idx, f in enumerate(request.filters):
        var_name = f"?v{idx}"

        # Security Check
        clean_prop_uri = f.property_uri.strip()
        if clean_prop_uri.startswith("^"):
            check_uri = clean_prop_uri[1:]
        else:
            check_uri = clean_prop_uri

        if not _is_safe_uri(check_uri):
            raise HTTPException(status_code=400, detail=f"Invalid Property URI: {check_uri}")

        # Handle Inverse Properties
        if clean_prop_uri.startswith("^"):
            prop = f"^<{clean_prop_uri[1:]}>"
        else:
            prop = f"<{clean_prop_uri}>"

        select_vars.append(var_name)

        # Logic for Graph Traversal (e.g., Vuln -> Software -> Vendor)
        if f.path_to_target:
            if not _is_safe_uri(f.path_to_target):
                raise HTTPException(status_code=400, detail="Invalid Path URI")

            intermediate_var = f"?inter_{idx}"
            where_clauses.append(f"?s {prop} {intermediate_var} .")
            where_clauses.append(f"{intermediate_var} <{f.path_to_target}> {var_name} .")
        else:
            where_clauses.append(f"?s {prop} {var_name} .")

        formatted_val = _format_value_for_sparql(f.value)
        val_clean = str(f.value).replace('"', '\\"')

        # --- Operator Logic ---

        if f.operator == FilterOperator.TRANSITIVE:
            # Semantic Hierarchical Search (e.g., find all child weaknesses)
            # We pop the last added simple triple because we need a Property Path instead
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

    # Optional Metadata for UI
    where_clauses.append("OPTIONAL { ?s rdfs:label ?label }")
    where_clauses.append("OPTIONAL { ?s schema:name ?label }")
    where_clauses.append("OPTIONAL { ?s a ?sType }")

    query_body = "\n".join(where_clauses + filter_clauses)

    # Note: We rely on run_sparql to prepend the global PREFIXES from config.py
    # This prevents namespace mismatch errors (e.g., davi-nist URLs).
    query = f"""
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

        # Label fallback logic
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
