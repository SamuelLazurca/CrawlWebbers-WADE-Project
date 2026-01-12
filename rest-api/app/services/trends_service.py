from typing import List, Optional

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import TrendPoint, GranularityEnum, AggregationType
from app.utils.sparql_queries import build_distribution_query, build_custom_analytics_query, \
    build_view_target_class_query
from app.utils.helpers import unpack_sparql_row, is_safe_uri


def _get_target_class(view_id: str) -> Optional[str]:
    """Helper to fetch the Target Class for a View (e.g. schema:Movie)"""
    if not view_id:
        return None
    query = build_view_target_class_query(view_id)
    results = run_sparql(query)
    if results:
        return unpack_sparql_row(results[0], "targetClass")
    return None


def get_distribution_query(
    target_property: str,
    view_id: Optional[str],
    granularity: GranularityEnum = GranularityEnum.NONE,
    limit: int = 100
) -> List[TrendPoint]:
    if not is_safe_uri(target_property):
        raise HTTPException(status_code=400, detail="Invalid Property URI")

    target_class = _get_target_class(view_id)

    query = build_distribution_query(target_property, target_class, granularity, limit)

    results = run_sparql(query)

    trend_data = []
    for row in results:
        label = unpack_sparql_row(row, "groupKey")
        count_val = unpack_sparql_row(row, "count", 0, int)
        trend_data.append(TrendPoint(label=label, value=count_val))

    return trend_data


def get_custom_analytics_query(
    dimension: str,
    metric: Optional[str],
    view_id: Optional[str],
    aggregation: AggregationType,
    limit: int = 20
) -> List[TrendPoint]:
    if not is_safe_uri(dimension):
        raise HTTPException(status_code=400, detail="Invalid Dimension URI")

    target_class = _get_target_class(view_id)

    query = build_custom_analytics_query(dimension, metric, target_class, aggregation, limit)

    try:
        results = run_sparql(query)
        data = []
        for row in results:
            label = unpack_sparql_row(row, "groupKey")
            if label and "http" in label and "/" in label:
                label = label.split("/")[-1].split("#")[-1]

            val = unpack_sparql_row(row, "val", 0, float)
            data.append(TrendPoint(label=label, value=val))
        return data

    except Exception as e:
        print(f"SPARQL Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error executing semantic query")
