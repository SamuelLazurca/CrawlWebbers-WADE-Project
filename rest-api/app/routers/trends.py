from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import TrendsResponse, GranularityEnum, AggregationType
from app.services.trends_service import get_distribution_query, get_custom_analytics_query

router = APIRouter()


@router.get("/distribution", response_model=TrendsResponse)
def get_property_distribution(
    target_property: str = Query(..., description="RDF Property URI"),
    view_id: Optional[str] = Query(None,
                                   description="The View Context (e.g. view_movielens_movies) to isolate data."),
    granularity: GranularityEnum = Query(GranularityEnum.NONE),
    limit: int = 100
):
    """
    **Preset Mode**: Simple distribution counting.
    If `view_id` is provided, analytics are scoped to that View's target class.
    """
    try:
        data = get_distribution_query(target_property, view_id, granularity, limit)
        total = sum(d.value for d in data)

        return TrendsResponse(
            property=target_property,
            granularity=granularity,
            total_records=total,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custom", response_model=TrendsResponse)
def get_custom_analytics(
    dimension: str = Query(..., description="X-Axis: Grouping property"),
    metric: str = Query(None, description="Y-Axis: Aggregation property"),
    view_id: Optional[str] = Query(None, description="The View Context to isolate data."),
    aggregation: AggregationType = Query(AggregationType.COUNT, description="Math operation"),
    limit: int = 100
):
    """
    **Custom Builder Mode**: Dynamic aggregation.
    """
    try:
        data = get_custom_analytics_query(dimension, metric, view_id, aggregation, limit)

        total = 0
        if data and aggregation in [AggregationType.COUNT, AggregationType.SUM]:
            total = sum(d.value for d in data)

        return TrendsResponse(
            property=f"{aggregation.value}({metric or 'records'}) by {dimension}",
            granularity=GranularityEnum.NONE,
            total_records=total,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics Error: {str(e)}")
