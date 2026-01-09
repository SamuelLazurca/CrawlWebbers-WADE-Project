from fastapi import APIRouter, Query, HTTPException
from app.models.schemas import TrendsResponse, GranularityEnum
from app.services.trends_service import get_distribution_query

router = APIRouter()


@router.get("/distribution", response_model=TrendsResponse)
def get_property_distribution(
    target_property: str = Query(..., description="RDF Property URI (e.g., http://schema.org/datePublished)"),
    granularity: GranularityEnum = Query(GranularityEnum.NONE, description="Time binning options for date fields"),
    limit: int = 100
):
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
