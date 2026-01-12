from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.models.schemas import GraphResponse
from app.services.graph_service import get_hierarchy_tree

router = APIRouter()


@router.get("/tree", response_model=GraphResponse)
def get_hierarchical_view(
    child_property: str = Query(..., description="The predicate connecting parent to child (e.g., skos:narrower)."),
    view_id: Optional[str] = Query(None,
                                   description="The View Context (e.g. view_nist_cwe) to isolate the hierarchy."),
    root_node: Optional[str] = Query(None, description="The root concept URI. If None, finds top-level concepts."),
    limit: int = 100
):
    """
    **Hierarchical View Extension**
    Fetches a tree structure for visualization.

    - **View Awareness:** If `view_id` is provided, the query restricts nodes to the View's `target_class`.
    - **Modularity:** Works for any hierarchy (CWE, SKOS taxonomies, Organization charts) defined in the ontology.
    """
    try:
        return get_hierarchy_tree(root_node, child_property, view_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
