from typing import List, Dict, Optional

from app.core.sparql import run_sparql
from app.models.schemas import GraphResponse, GraphNode, GraphLink


def get_node_neighborhood(
    resource_uri: str,
    limit: int = 100
) -> GraphResponse:
    """
    Fetches the immediate graph neighborhood (1-hop) for a specific resource.
    """
    # Note: Global PREFIXES are injected by run_sparql, so we don't need to repeat them here.
    query = f"""
    SELECT ?s ?p ?o ?sLabel ?oLabel ?sType ?oType
    WHERE {{
        BIND(<{resource_uri}> AS ?center)

        {{
            # Outgoing Edges: Center -> ?p -> ?o
            ?center ?p ?o .
            BIND(?center AS ?s)
        }}
        UNION
        {{
            # Incoming Edges: ?s -> ?p -> Center
            ?s ?p ?center .
            BIND(?center AS ?o)
        }}

        # Get Labels
        OPTIONAL {{ ?s rdfs:label ?sLabel }}
        OPTIONAL {{ ?s schema:name ?sLabel }}
        OPTIONAL {{ ?s skos:prefLabel ?sLabel }}

        OPTIONAL {{ ?o rdfs:label ?oLabel }}
        OPTIONAL {{ ?o schema:name ?oLabel }}
        OPTIONAL {{ ?o skos:prefLabel ?oLabel }}

        # Get Types for coloring
        OPTIONAL {{ ?s a ?sType }}
        OPTIONAL {{ ?o a ?oType }}
    }}
    LIMIT {limit}
    """

    results = run_sparql(query)
    return _transform_sparql_to_graph(results, center_node=resource_uri)


def get_hierarchy_tree(
    root_node: Optional[str],
    child_property: str,
    limit: int = 100
) -> GraphResponse:
    """
    Fetches a tree structure based on a parent-child property (e.g., skos:narrower).
    - If root_node is provided: Fetches its children.
    - If root_node is None: Tries to find 'Top Concepts' (nodes with no parents).
    """

    # 1. Build the specific WHERE clause based on whether we have a root
    if root_node:
        # Fetch children of a specific root
        where_logic = f"""
            BIND(<{root_node}> AS ?parent)
            ?parent <{child_property}> ?child .
        """
    else:
        # Fetch Top Roots (Nodes that are subjects of the property but never objects)
        # This assumes the property points Down (Parent -> Child)
        where_logic = f"""
            ?parent <{child_property}> ?child .
            FILTER NOT EXISTS {{ ?grandparent <{child_property}> ?parent }}
        """

    query = f"""
    SELECT DISTINCT ?parent ?child ?parentLabel ?childLabel ?parentType ?childType
    WHERE {{
        {where_logic}

        # Labels for Parent
        OPTIONAL {{ ?parent rdfs:label ?parentLabel }}
        OPTIONAL {{ ?parent schema:name ?parentLabel }}
        OPTIONAL {{ ?parent skos:prefLabel ?parentLabel }}
        OPTIONAL {{ ?parent a ?parentType }}

        # Labels for Child
        OPTIONAL {{ ?child rdfs:label ?childLabel }}
        OPTIONAL {{ ?child schema:name ?childLabel }}
        OPTIONAL {{ ?child skos:prefLabel ?childLabel }}
        OPTIONAL {{ ?child a ?childType }}
    }}
    LIMIT {limit}
    """

    results = run_sparql(query)

    # We map this result structure to the GraphResponse format manually
    # because the query variable names (?parent, ?child) differ from the neighborhood (?s, ?o)
    nodes_map: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    for row in results:
        p_uri = row["parent"]["value"]
        c_uri = row["child"]["value"]

        # Ensure Parent Node exists
        if p_uri not in nodes_map:
            nodes_map[p_uri] = GraphNode(
                id=p_uri,
                label=_get_label(row.get("parentLabel"), p_uri),
                group=_get_group(row.get("parentType"))
            )

        # Ensure Child Node exists
        if c_uri not in nodes_map:
            nodes_map[c_uri] = GraphNode(
                id=c_uri,
                label=_get_label(row.get("childLabel"), c_uri),
                group=_get_group(row.get("childType"))
            )

        # Create Link (Parent -> Child)
        # link_key = f"{p_uri}-{c_uri}"
        # Simple check to avoid duplicates if SPARQL returns multiples
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


# --- Helpers ---

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
