from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.models.schemas import GraphResponse
from app.services.graph_service import get_node_neighborhood

router = APIRouter()

@router.get("/neighborhood", response_model=GraphResponse)
def get_graph_neighborhood(
    resource_uri: str = Query(..., description="The full URI of the center node"),
    view_id: Optional[str] = Query(None, description="Optional: View Context to highlight relevant nodes."),
    limit: int = 50
):
    """
    **Graph/Network Extension**
    Fetches the immediate neighborhood of a node for Force-Directed or 3D Visualizations.
    """
    try:
        return get_node_neighborhood(resource_uri, view_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
