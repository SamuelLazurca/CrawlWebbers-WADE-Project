from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import TrendsResponse, GranularityEnum, AggregationType
from app.services.trends_service import get_distribution_query, get_custom_analytics_query

router = APIRouter()


@router.get("/distribution", response_model=TrendsResponse)
def get_property_distribution(
    target_property: str = Query(..., description="RDF Property URI"),
    granularity: GranularityEnum = Query(GranularityEnum.NONE),
    limit: int = 100
):
    """
    **Preset Mode**: Simple distribution counting.
    Useful for 'Quick Start' charts defined in VisualizationOptions.
    """
    try:
        data = get_distribution_query(target_property, granularity, limit)
        total = sum(d.count for d in data)

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
    dimension: str = Query(..., description="X-Axis: The grouping property URI (must be a Dimension)"),
    metric: str = Query(None,
                        description="Y-Axis: The property to aggregate (must be a Metric). Defaults to Count if None."),
    aggregation: AggregationType = Query(AggregationType.COUNT,
                                         description="Math operation (AVG, SUM, COUNT, etc.)"),
    limit: int = 100
):
    """
    **Custom Builder Mode**: Dynamic aggregation.
    Allows queries like 'Average Rating by Genre' or 'Max CVSS Score by Vendor'.
    """
    try:
        # This function will need to be implemented in your services update
        data = get_custom_analytics_query(dimension, metric, aggregation, limit)

        # Calculate total for reference (if it makes sense for the aggregation)
        total = sum(d.count for d in data) if data else 0

        return TrendsResponse(
            property=f"{aggregation.value}({metric or 'records'}) by {dimension}",
            granularity=GranularityEnum.NONE,
            total_records=total,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics Error: {str(e)}")
