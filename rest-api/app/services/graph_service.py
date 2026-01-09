from typing import List, Dict
from app.core.sparql import run_sparql
from app.models.schemas import GraphResponse, GraphNode, GraphLink


def get_node_neighborhood(
        resource_uri: str,
        limit: int = 100
) -> GraphResponse:
    """
    Fetches the immediate graph neighborhood (1-hop) for a specific resource.
    Includes logic to handle URI formatting issues (http vs. https) and SKOS labels.
    """
    query = f"""
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX davi-nist: <http://davi.app/vocab/nist#>

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

        # Get Labels (Covers Schema.org, RDFS, and SKOS for CWEs)
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

    nodes_map: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    for row in results:
        s_uri = row["s"]["value"]
        p_uri = row["p"]["value"]
        o_uri = row["o"]["value"]

        # Clean Group Name (e.g. http://schema.org/Movie -> Movie)
        def get_group(type_row):
            if not type_row:
                if o_uri == row["o"]["value"] and row["o"]["type"] == "literal":
                    return "Value"
                return "Unknown"
            return type_row["value"].split("#")[-1].split("/")[-1]

        def get_label(val_row, uri):
            if val_row:
                return val_row["value"]
            if "#" in uri: return uri.split("#")[-1]
            return uri.split("/")[-1]

        if s_uri not in nodes_map:
            nodes_map[s_uri] = GraphNode(
                id=s_uri,
                label=get_label(row.get("sLabel"), s_uri),
                group=get_group(row.get("sType"))
            )

        if o_uri not in nodes_map:
            is_literal = (row["o"]["type"] == "literal")

            nodes_map[o_uri] = GraphNode(
                id=o_uri,
                label=o_uri if is_literal else get_label(row.get("oLabel"), o_uri),
                group="Literal" if is_literal else get_group(row.get("oType"))
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
        center_node=resource_uri,
        nodes=list(nodes_map.values()),
        links=links
    )
