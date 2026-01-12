from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.models.schemas import FilterRequest, FilterResultItem
from app.services.filter_service import build_intelligent_query

router = APIRouter()


@router.post("/advanced", response_model=List[FilterResultItem])
def intelligent_search(
    request: FilterRequest = Body(..., description="Define facets, ranges, and semantic inference rules.")
):
    """
    **Intelligent Filtering Extension**

    Perform multi-faceted semantic search leveraging ontology hierarchy, graph traversal, and inverse relations.

    **View Context:**
    This endpoint works in the context of a specific **Data View**.
    The `target_class` parameter should match the `target_class` of the View you are querying
    (e.g., `https://purl.org/davi/vocab/nist#Vulnerability`).

    **Supported Operators:**
    - Comparison: `=`, `!=`, `>`, `<`
    - String: `CONTAINS`, `NOT_CONTAINS` (Case-insensitive)
    - Semantic: `TRANSITIVE` (Finds all children of a concept using `skos:broader` or `rdfs:subClassOf`)
    """
    try:
        return build_intelligent_query(request)
    except Exception as e:
        # Log the full error in production, return a simple message to the client
        raise HTTPException(status_code=500, detail=f"SPARQL Generation Error: {str(e)}")
