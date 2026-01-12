from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.services.compare_service import compare_entities
from app.models.schemas import ComparisonResponse

router = APIRouter()


@router.get("/", response_model=ComparisonResponse)
def compare_resources(
        uri_a: str = Query(..., description="Full URI of the first resource"),
        uri_b: str = Query(..., description="Full URI of the second resource"),
        view_id: Optional[str] = Query(None,
                                       description="Optional: The View URI (e.g., view_movielens_movies) to use for label overrides.")
):
    """
    **Compare Extension**

    Performs a side-by-side comparison of two RDF resources.

    **View Awareness:**
    If `view_id` is provided, the comparison will use the specific labels defined
    in that View (e.g., showing 'Release Year' instead of generic 'Date').
    """
    try:
        return compare_entities(uri_a, uri_b, view_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
