from fastapi import APIRouter, Query, HTTPException
from app.services.compare_service import compare_entities
from app.models.schemas import ComparisonResponse

router = APIRouter()


@router.get("/", response_model=ComparisonResponse)
def compare_resources(
        uri_a: str = Query(..., description="Full URI of the first resource"),
        uri_b: str = Query(..., description="Full URI of the second resource")
):
    """
    **Compare Extension**

    Performs a side-by-side comparison of two RDF resources.
    Returns:
    - **Common Properties**: Intersection (What they share, e.g., both are 'Action' movies).
    - **Unique to A**: Difference (e.g., A was released in 1995).
    - **Unique to B**: Difference (e.g., B was released in 1999).
    """
    try:
        return compare_entities(uri_a, uri_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
