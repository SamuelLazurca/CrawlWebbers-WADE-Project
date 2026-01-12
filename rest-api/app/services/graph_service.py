from typing import List, Dict, Optional

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import GraphResponse, GraphNode, GraphLink
from app.utils.sparql_queries import (
    build_neighborhood_query,
    build_hierarchy_query,
    build_view_target_class_query
)
from app.utils.helpers import unpack_sparql_row, is_safe_uri


def _get_target_class(view_id: str) -> Optional[str]:
    """Helper to fetch the Target Class for a View"""
    if not view_id:
        return None
    results = run_sparql(build_view_target_class_query(view_id))
    if results:
        return unpack_sparql_row(results[0], "targetClass")
    return None


def get_node_neighborhood(resource_uri: str, view_id: Optional[str], limit: int = 100) -> GraphResponse:
    if not is_safe_uri(resource_uri):
        raise HTTPException(status_code=400, detail="Invalid Resource URI")

    target_class = _get_target_class(view_id)

    query = build_neighborhood_query(resource_uri, target_class, limit)
    results = run_sparql(query)

    return _transform_sparql_to_graph(results, center_node=resource_uri)


def get_hierarchy_tree(
        root_node: Optional[str],
        child_property: str,
        view_id: Optional[str],
        limit: int = 100
) -> GraphResponse:
    if not is_safe_uri(child_property):
        raise HTTPException(status_code=400, detail="Invalid Property URI")

    target_class = _get_target_class(view_id)

    query = build_hierarchy_query(child_property, root_node, target_class, limit)
    results = run_sparql(query)

    nodes_map: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    for row in results:
        p_uri = unpack_sparql_row(row, "parent")
        c_uri = unpack_sparql_row(row, "child")

        if not p_uri or not c_uri:
            continue

        if p_uri not in nodes_map:
            nodes_map[p_uri] = GraphNode(
                id=p_uri,
                label=unpack_sparql_row(row, "parentLabel", p_uri.split("/")[-1]),
                group=unpack_sparql_row(row, "parentType", "Node")
            )
        if c_uri not in nodes_map:
            nodes_map[c_uri] = GraphNode(
                id=c_uri,
                label=unpack_sparql_row(row, "childLabel", c_uri.split("/")[-1]),
                group=unpack_sparql_row(row, "childType", "Node")
            )

        link_key = (p_uri, c_uri)
        if not any(l.source == p_uri and l.target == c_uri for l in links):
            links.append(GraphLink(
                source=p_uri,
                target=c_uri,
                relationship=child_property.split("#")[-1].split("/")[-1]
            ))

    return GraphResponse(
        center_node=root_node if root_node else "root",
        nodes=list(nodes_map.values()),
        links=links
    )


def _transform_sparql_to_graph(results, center_node) -> GraphResponse:
    nodes_map: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    for row in results:
        s_uri = unpack_sparql_row(row, "s")
        p_uri = unpack_sparql_row(row, "p")
        o_uri = unpack_sparql_row(row, "o")

        if not s_uri or not o_uri:
            continue

        if s_uri not in nodes_map:
            nodes_map[s_uri] = GraphNode(
                id=s_uri,
                label=unpack_sparql_row(row, "sLabel", s_uri.split("/")[-1]),
                group=unpack_sparql_row(row, "sType", "Unknown")
            )

        if o_uri not in nodes_map:
            is_literal = (row.get("o", {}).get("type") == "literal")
            nodes_map[o_uri] = GraphNode(
                id=o_uri,
                label=o_uri if is_literal else unpack_sparql_row(row, "oLabel", o_uri.split("/")[-1]),
                group="Literal" if is_literal else unpack_sparql_row(row, "oType", "Unknown")
            )

        rel_label = p_uri.split("#")[-1].split("/")[-1]

        if not any(l.source == s_uri and l.target == o_uri and l.relationship == rel_label for l in links):
            links.append(GraphLink(
                source=s_uri,
                target=o_uri,
                relationship=rel_label
            ))

    return GraphResponse(
        center_node=center_node,
        nodes=list(nodes_map.values()),
        links=links
    )
