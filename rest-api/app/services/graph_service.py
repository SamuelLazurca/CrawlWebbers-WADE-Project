from typing import List, Dict, Optional

from app.core.sparql import run_sparql
from app.models.schemas import GraphResponse, GraphNode, GraphLink
from app.utils.sparql_queries import build_neighborhood_query, build_hierarchy_query


def get_node_neighborhood(resource_uri: str, limit: int = 100) -> GraphResponse:
    query = build_neighborhood_query(resource_uri, limit)
    results = run_sparql(query)
    return _transform_sparql_to_graph(results, center_node=resource_uri)


def get_hierarchy_tree(
    root_node: Optional[str],
    child_property: str,
    limit: int = 100
) -> GraphResponse:
    query = build_hierarchy_query(child_property, root_node, limit)
    results = run_sparql(query)

    nodes_map: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    for row in results:
        p_uri = row["parent"]["value"]
        c_uri = row["child"]["value"]

        if p_uri not in nodes_map:
            nodes_map[p_uri] = GraphNode(
                id=p_uri,
                label=_get_label(row.get("parentLabel"), p_uri),
                group=_get_group(row.get("parentType"))
            )
        if c_uri not in nodes_map:
            nodes_map[c_uri] = GraphNode(
                id=c_uri,
                label=_get_label(row.get("childLabel"), c_uri),
                group=_get_group(row.get("childType"))
            )

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
        s_uri = row["s"]["value"]
        p_uri = row["p"]["value"]
        o_uri = row["o"]["value"]

        if s_uri not in nodes_map:
            nodes_map[s_uri] = GraphNode(
                id=s_uri,
                label=_get_label(row.get("sLabel"), s_uri),
                group=_get_group(row.get("sType"))
            )

        if o_uri not in nodes_map:
            is_literal = (row["o"]["type"] == "literal")
            nodes_map[o_uri] = GraphNode(
                id=o_uri,
                label=o_uri if is_literal else _get_label(row.get("oLabel"), o_uri),
                group="Literal" if is_literal else _get_group(row.get("oType"))
            )

        rel_label = p_uri.split("#")[-1].split("/")[-1]

        link_exists = any(
            l.source == s_uri and l.target == o_uri and l.relationship == rel_label
            for l in links
        )

        if not link_exists:
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


def _get_group(type_row):
    if not type_row:
        return "Unknown"
    # Extract class name from URI (e.g., http://schema.org/Movie -> Movie)
    return type_row["value"].split("#")[-1].split("/")[-1]


def _get_label(val_row, uri):
    if val_row:
        return val_row["value"]
    # Fallback to URI fragment
    if "#" in uri: return uri.split("#")[-1]
    return uri.split("/")[-1]
