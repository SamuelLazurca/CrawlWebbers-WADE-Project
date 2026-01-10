from fastapi import APIRouter, Query, HTTPException
from app.models.schemas import GraphResponse
from app.services.graph_service import get_hierarchy_tree

router = APIRouter()

@router.get("/tree", response_model=GraphResponse)
def get_hierarchical_view(
    root_node: str = Query(None, description="The root concept URI. If None, finds top-level concepts."),
    child_property: str = Query(..., description="The predicate connecting parent to child (e.g., skos:narrower)."),
    limit: int = 100
):
    """
    **Hierarchical View Extension**
    Fetches a tree structure for visualization (e.g., CWE Weakness Hierarchy).
    """
    try:
        return get_hierarchy_tree(root_node, child_property, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
