from typing import List, Optional

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import TrendPoint, GranularityEnum, AggregationType
from app.utils.sparql_queries import build_distribution_query, build_custom_analytics_query


def _is_safe_uri(uri: str) -> bool:
    return not any(c in uri for c in [" ", ";", "{", "}", "\\", '"', "'"])


def get_distribution_query(
    target_property: str,
    granularity: GranularityEnum = GranularityEnum.NONE,
    limit: int = 100
) -> List[TrendPoint]:
    if not _is_safe_uri(target_property):
        raise HTTPException(status_code=400, detail="Invalid Property URI")

    # Granularity logic is now handled inside the query builder
    query = build_distribution_query(target_property, granularity, limit)
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
    limit: int = 20
) -> List[TrendPoint]:
    if not _is_safe_uri(dimension):
        raise HTTPException(status_code=400, detail="Invalid Dimension URI")
    if metric and not _is_safe_uri(metric):
        raise HTTPException(status_code=400, detail="Invalid Metric URI")

    query = build_custom_analytics_query(dimension, metric, aggregation, limit)

    try:
        results = run_sparql(query)
        data = []
        for row in results:
            label = row["groupKey"]["value"]
            if "http" in label and "/" in label:
                label = label.split("/")[-1].split("#")[-1]

            raw_val = row["val"]["value"]
            try:
                val = float(raw_val) if "." in str(raw_val) else int(raw_val)
            except (ValueError, TypeError):
                val = 0
            data.append(TrendPoint(label=label, count=val))
        return data

    except Exception as e:
        print(f"SPARQL Error: {str(e)}\nQuery: {query}")
        raise HTTPException(status_code=500, detail="Error executing semantic query")
