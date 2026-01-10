from typing import List, Optional

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import TrendPoint, GranularityEnum, AggregationType


def _is_safe_uri(uri: str) -> bool:
    """Basic injection check."""
    return not any(c in uri for c in [" ", ";", "{", "}", "\\", '"', "'"])


def get_distribution_query(
    target_property: str,
    granularity: GranularityEnum = GranularityEnum.NONE,
    limit: int = 100
) -> List[TrendPoint]:
    """
    **Legacy/Preset Mode:**
    Calculates simple frequency distribution (COUNT) for a single property.
    Used by the 'Preset' visualizations.
    """
    if not _is_safe_uri(target_property):
        raise HTTPException(status_code=400, detail="Invalid Property URI")

    # Handles Date Grouping logic
    bind_logic = "BIND(?rawVal as ?groupKey)"
    if granularity == GranularityEnum.YEAR:
        bind_logic = "BIND(STR(YEAR(?rawVal)) as ?groupKey)"
    elif granularity == GranularityEnum.MONTH:
        bind_logic = """
            BIND(CONCAT(STR(YEAR(?rawVal)), "-", STR(MONTH(?rawVal))) as ?groupKey)
        """
    elif granularity == GranularityEnum.DAY:
        # Use SUBSTR for ISO dates (safest cross-db method)
        bind_logic = "BIND(SUBSTR(STR(?rawVal), 1, 10) as ?groupKey)"

    query = f"""
    SELECT ?groupKey (COUNT(?s) as ?count)
    WHERE {{
        ?s <{target_property}> ?rawVal .
        FILTER(BOUND(?rawVal))

        {bind_logic}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?count)
    LIMIT {limit}
    """

    results = run_sparql(query)

    trend_data = []
    for row in results:
        label = row["groupKey"]["value"]
        try:
            count_val = int(row["count"]["value"])
        except ValueError:
            count_val = 0

        trend_data.append(TrendPoint(label=label, count=count_val))

    return trend_data


def get_custom_analytics_query(
    dimension: str,
    metric: Optional[str],
    aggregation: AggregationType,
    limit: int = 100
) -> List[TrendPoint]:
    """
    **Custom Builder Mode:**
    Generates a dynamic aggregation query based on Dimension (X-Axis) and Metric (Y-Axis).
    Uses Property Paths `(!rdf:type)*` to find properties that might be nested.
    """
    if not _is_safe_uri(dimension):
        raise HTTPException(status_code=400, detail="Invalid Dimension URI")

    if metric and not _is_safe_uri(metric):
        raise HTTPException(status_code=400, detail="Invalid Metric URI")

    # 1. Determine Aggregation Function
    agg_map = {
        AggregationType.COUNT: "COUNT",
        AggregationType.SUM: "SUM",
        AggregationType.AVG: "AVG",
        AggregationType.MAX: "MAX",
        AggregationType.MIN: "MIN"
    }
    agg_func = agg_map.get(aggregation, "COUNT")

    # 2. Build Metric Logic
    # If no metric is provided, we just count the occurrences of the dimension (Frequency)
    if not metric:
        metric_logic = ""
        selection = "(COUNT(?s) as ?val)"
    else:
        # Semantic Path: Traverse graph to find the metric value (e.g., Vuln -> CVSS -> Score)
        # (!rdf:type)+ means "follow any predicate (except type) 1 or more times"
        metric_logic = f"?s (!rdf:type)+ <{metric}> ?metricRaw ."
        selection = f"({agg_func}(xsd:decimal(?metricRaw)) as ?val)"

    # 3. Build Dimension Logic
    # We try to fetch a human-readable label for the dimension URI (e.g., Vendor Name)
    dimension_logic = f"""
        ?s (!rdf:type)+ <{dimension}> ?dimVal .

        OPTIONAL {{ 
            ?dimVal rdfs:label ?dimLabel 
        }}
        OPTIONAL {{ 
            ?dimVal schema:name ?dimLabel 
        }}

        BIND(COALESCE(?dimLabel, ?dimVal) as ?groupKey)
    """

    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?groupKey {selection}
    WHERE {{
        {dimension_logic}
        {metric_logic}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?val)
    LIMIT {limit}
    """

    results = run_sparql(query)

    data = []
    for row in results:
        label = row["groupKey"]["value"]

        # Parse the result value (might be of type float for AVG, int for COUNT)
        raw_val = row["val"]["value"]
        try:
            if "." in raw_val:
                val = float(raw_val)
            else:
                val = int(raw_val)
        except ValueError:
            val = 0

        data.append(TrendPoint(label=label, count=val))

    return data
