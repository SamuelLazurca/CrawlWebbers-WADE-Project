from typing import List
from app.core.sparql import run_sparql
from app.models.schemas import TrendPoint, GranularityEnum


def get_distribution_query(
    target_property: str,
    granularity: GranularityEnum = GranularityEnum.NONE,
    limit: int = 100
) -> List[TrendPoint]:
    """
    Generates a GROUP BY query to calculate frequency distributions.
    Handles specialized logic for Date fields (Year/Month extraction).
    """
    if not (target_property.startswith("http") or ":" in target_property):
        raise ValueError(f"Invalid Property URI: {target_property}")

    bind_logic = "BIND(?rawVal as ?groupKey)"

    if granularity == GranularityEnum.YEAR:
        bind_logic = "BIND(STR(YEAR(?rawVal)) as ?groupKey)"
    elif granularity == GranularityEnum.MONTH:
        bind_logic = """
            BIND(CONCAT(STR(YEAR(?rawVal)), "-", STR(MONTH(?rawVal))) as ?groupKey)
        """
    elif granularity == GranularityEnum.DAY:
        bind_logic = "BIND(STRDT(STR(?rawVal), xsd:date) as ?groupKey)"

    query = f"""
    SELECT ?groupKey (COUNT(?s) as ?count)
    WHERE {{
        ?s <{target_property}> ?rawVal .
        FILTER(BOUND(?rawVal))

        {bind_logic}
    }}
    GROUP BY ?groupKey
    ORDER BY ?groupKey
    LIMIT {limit}
    """

    results = run_sparql(query)

    trend_data = []
    for row in results:
        label = row["groupKey"]["value"]
        count = int(row["count"]["value"])

        #TODO: For now, we return the raw value as the label.
        trend_data.append(TrendPoint(label=label, count=count))

    return trend_data
