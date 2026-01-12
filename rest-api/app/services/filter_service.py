import logging
import re
from typing import List, Union

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import FilterRequest, FilterOperator, FilterResultItem
from app.utils.helpers import is_safe_uri

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _format_value_for_sparql(value: Union[str, int, float, bool]) -> str:
    """
    Formats Python values into SPARQL literals.
    """
    if isinstance(value, bool):
        return f"'{str(value).lower()}'^^xsd:boolean"

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
    active_paths = {}

    if not is_safe_uri(request.target_class):
        raise HTTPException(status_code=400, detail="Invalid Target Class URI")

    # 1. Base Structure
    where_clauses = [f"?s a <{request.target_class}> ."]
    filter_clauses = []

    # NEW: We need the text prefix for the optimization to work
    prefixes = "PREFIX text: <http://jena.apache.org/text#>\n"

    for idx, f in enumerate(request.filters):
        var_name = f"?v{idx}"

        clean_prop_uri = f.property_uri.strip()

        # Handle Inverse Properties
        if clean_prop_uri.startswith("^"):
            check_uri = clean_prop_uri[1:]
            prop = f"^<{check_uri}>"
            raw_prop = f"<{check_uri}>"  # Used for text:query check
        else:
            check_uri = clean_prop_uri
            prop = f"<{check_uri}>"
            raw_prop = prop

        if not is_safe_uri(check_uri):
            raise HTTPException(status_code=400, detail=f"Invalid Property URI: {check_uri}")

        select_vars.append(var_name)

        val_clean = str(f.value).replace('"', '\\"')
        formatted_val = _format_value_for_sparql(f.value)

        # ---------------------------------------------------------
        # OPTIMIZATION LOGIC
        # ---------------------------------------------------------

        if f.operator == FilterOperator.TRANSITIVE:
            # Hierarchy Logic (Tree Search)
            target_node = f"<{val_clean}>" if "http" in str(f.value) else f"'{val_clean}'"

            where_clauses.append(f"""
                ?s {prop} ?concept .
                ?concept (skos:broader*|rdfs:subClassOf*) {target_node} .
                BIND({target_node} AS {var_name}) 
            """)

        elif f.operator == FilterOperator.CONTAINS:
            # TEXT INDEX LOGIC (The Performance Boost)
            # Instead of scanning all rows with regex, we ask the Index first.
            # Syntax: ?s text:query ( property "search_term" )

            # Note: We still include the standard triple `?s {prop} {var_name}`
            # below to ensure we bind the variable for display.

            # Optimization: "Find Subjects ?s where Property matches Value"
            where_clauses.append(f"?s text:query ({raw_prop} \"{val_clean}\") .")

            # Standard binding (retrieves the actual text to show in the UI)
            if f.path_to_target:
                # Complex paths (nested objects) are harder to optimize with simple text:query
                # We fall back to standard logic for paths
                pass
            else:
                # We still bind the variable, but the heavy lifting was done by text:query
                where_clauses.append(f"?s {prop} {var_name} .")

        else:
            # STANDARD LOGIC (Numeric, Dates, Exact Match)
            if f.path_to_target:
                if not is_safe_uri(f.path_to_target):
                    raise HTTPException(status_code=400, detail="Invalid Path URI")

                path_key = f.property_uri

                if path_key in active_paths:
                    intermediate_var = active_paths[path_key]
                else:
                    intermediate_var = f"?inter_{idx}"
                    active_paths[path_key] = intermediate_var
                    where_clauses.append(f"?s {prop} {intermediate_var} .")

                where_clauses.append(f"{intermediate_var} <{f.path_to_target}> {var_name} .")
            else:
                where_clauses.append(f"?s {prop} {var_name} .")

            # Apply Standard Filters (Regex, >, <, =)
            if f.operator == FilterOperator.CONTAINS:
                # Fallback for complex paths that skipped the optimization block above
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
    where_clauses.append("OPTIONAL { ?s skos:prefLabel ?label }")
    where_clauses.append("OPTIONAL { ?s a ?sType }")

    query_body = "\n".join(where_clauses + filter_clauses)

    # 3. Final Assembly
    query = f"""
    {prefixes}
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
