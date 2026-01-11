from typing import Optional
from app.models.schemas import GranularityEnum, AggregationType


def build_all_datasets_query() -> str:
    return """
    SELECT ?ds ?id ?name ?desc ?url ?date ?sizeBytes ?numFiles ?numDownloads ?uploadedBy ?uploadedByUrl
    WHERE {
        ?ds a davi-meta:Dataset ;
            dcterms:identifier ?id ;
            schema:name ?name ;
            schema:description ?desc ;
            davi-meta:sizeBytes ?sizeBytes ;
            davi-meta:fileCount ?numFiles ;
            davi-meta:downloadCount ?numDownloads .
        OPTIONAL { ?ds schema:url ?url }
        OPTIONAL { ?ds schema:dateCreated ?date }
        OPTIONAL { 
            ?ds davi-meta:uploader ?uploader .
            ?uploader schema:name ?uploadedBy .
            OPTIONAL { ?uploader schema:url ?uploadedByUrl }
        }
    }
    """

def build_viz_config_query(dataset_uri: str) -> str:
    return f"""
    SELECT ?viz ?vizLabel ?vizDesc ?opt ?optLabel ?targetProp
    WHERE {{
        <{dataset_uri}> davi-meta:supportsVisualization ?viz .
        ?viz davi-meta:uiLabel ?vizLabel .
        OPTIONAL {{ ?viz dcterms:description ?vizDesc }}
        OPTIONAL {{
            ?viz davi-meta:hasOption ?opt .
            ?opt davi-meta:uiLabel ?optLabel ;
                 davi-meta:targetProperty ?targetProp .
        }}
    }}
    ORDER BY ?vizLabel
    """

def build_analytics_config_query(dataset_uri: str) -> str:
    return f"""
    SELECT DISTINCT ?prop ?label ?type
    WHERE {{
        {{
            <{dataset_uri}> davi-meta:hasDimension ?prop .
            BIND("dimension" AS ?type)
        }}
        UNION
        {{
            <{dataset_uri}> davi-meta:hasMetric ?prop .
            BIND("metric" AS ?type)
        }}
        OPTIONAL {{ ?prop davi-meta:uiLabel ?label }}
    }}
    ORDER BY ?label
    """


def build_neighborhood_query(resource_uri: str, limit: int) -> str:
    return f"""
    SELECT ?s ?p ?o ?sLabel ?oLabel ?sType ?oType
    WHERE {{
        BIND(<{resource_uri}> AS ?center)
        {{
            ?center ?p ?o .
            BIND(?center AS ?s)
        }}
        UNION
        {{
            ?s ?p ?center .
            BIND(?center AS ?o)
        }}
        OPTIONAL {{ ?s rdfs:label ?sLabel }}
        OPTIONAL {{ ?s schema:name ?sLabel }}
        OPTIONAL {{ ?s skos:prefLabel ?sLabel }}
        OPTIONAL {{ ?o rdfs:label ?oLabel }}
        OPTIONAL {{ ?o schema:name ?oLabel }}
        OPTIONAL {{ ?o skos:prefLabel ?oLabel }}
        OPTIONAL {{ ?s a ?sType }}
        OPTIONAL {{ ?o a ?oType }}
    }}
    LIMIT {limit}
    """

def build_hierarchy_query(child_property: str, root_node: Optional[str] = None, limit: int = 100) -> str:
    if root_node:
        where_logic = f"""
            BIND(<{root_node}> AS ?parent)
            ?parent <{child_property}> ?child .
        """
    else:
        where_logic = f"""
            ?parent <{child_property}> ?child .
            FILTER NOT EXISTS {{ ?grandparent <{child_property}> ?parent }}
        """

    return f"""
    SELECT DISTINCT ?parent ?child ?parentLabel ?childLabel ?parentType ?childType
    WHERE {{
        {where_logic}
        OPTIONAL {{ ?parent rdfs:label ?parentLabel }}
        OPTIONAL {{ ?parent schema:name ?parentLabel }}
        OPTIONAL {{ ?parent skos:prefLabel ?parentLabel }}
        OPTIONAL {{ ?parent a ?parentType }}
        OPTIONAL {{ ?child rdfs:label ?childLabel }}
        OPTIONAL {{ ?child schema:name ?childLabel }}
        OPTIONAL {{ ?child skos:prefLabel ?childLabel }}
        OPTIONAL {{ ?child a ?childType }}
    }}
    LIMIT {limit}
    """


def build_distribution_query(target_property: str, granularity: GranularityEnum, limit: int) -> str:
    # Logic for Date Grouping moved here to keep Service clean
    bind_logic = "BIND(?rawVal as ?groupKey)"
    if granularity == GranularityEnum.YEAR:
        bind_logic = "BIND(STR(YEAR(?rawVal)) as ?groupKey)"
    elif granularity == GranularityEnum.MONTH:
        bind_logic = """BIND(CONCAT(STR(YEAR(?rawVal)), "-", STR(MONTH(?rawVal))) as ?groupKey)"""
    elif granularity == GranularityEnum.DAY:
        bind_logic = "BIND(SUBSTR(STR(?rawVal), 1, 10) as ?groupKey)"

    return f"""
    SELECT ?groupKey (COUNT(?s) as ?count)
    WHERE {{
        ?s <{target_property}> ?rawVal .
        FILTER(BOUND(?rawVal))
        {bind_logic}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?count)
    LIMIT {limit}
    """

def build_custom_analytics_query(dimension: str, metric: Optional[str], aggregation: AggregationType, limit: int) -> str:
    if not metric:
        selection = "(COUNT(DISTINCT ?s) as ?val)"
        metric_pattern = ""
    else:
        selection = f"({aggregation.value}(xsd:decimal(?metricRaw)) as ?val)"
        metric_pattern = f"?s <{metric}> ?metricRaw ."

    return f"""
    SELECT ?groupKey {selection}
    WHERE {{
        ?s <{dimension}> ?dimVal .
        OPTIONAL {{ ?dimVal rdfs:label | schema:name ?dimLabel }}
        BIND(COALESCE(STR(?dimLabel), STR(?dimVal)) as ?groupKey)
        {metric_pattern}
        {"FILTER(BOUND(?metricRaw))" if metric else ""}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?val)
    LIMIT {limit}
    """


def build_comparison_query(uri_a: str, uri_b: str, limit: int = 500) -> str:
    """
    Fetches all properties/values for two entities simultaneously.
    Returns ?source ('A' or 'B') to allow Python to split them.
    """
    return f"""
    SELECT ?source ?p ?o ?pLabel ?oLabel
    WHERE {{
        {{
            <{uri_a}> ?p ?o .
            BIND("A" AS ?source)
        }}
        UNION
        {{
            <{uri_b}> ?p ?o .
            BIND("B" AS ?source)
        }}

        # Fetch Labels for Properties
        OPTIONAL {{ ?p rdfs:label ?pLabel }}
        OPTIONAL {{ ?p schema:name ?pLabel }}
        OPTIONAL {{ ?p skos:prefLabel ?pLabel }}

        # Fetch Labels for Object Values (if they are URIs)
        OPTIONAL {{ 
            FILTER(isURI(?o))
            ?o rdfs:label ?oLabel 
        }}
        OPTIONAL {{ 
            FILTER(isURI(?o))
            ?o schema:name ?oLabel 
        }}
    }}
    LIMIT {limit}
    """
