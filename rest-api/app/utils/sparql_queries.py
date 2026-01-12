from typing import Optional

from app.models.schemas import GranularityEnum, AggregationType


def build_all_datasets_query() -> str:
    return """
    SELECT ?ds ?id ?name ?desc ?url ?date ?sizeBytes ?numFiles ?numDownloads ?uploadedBy ?uploadedByUrl
    WHERE {
        ?ds a davi-meta:Dataset ;
            dcterms:identifier ?id ;
            schema:name ?name ;
            schema:description ?desc .

        OPTIONAL { ?ds davi-meta:sizeBytes ?sizeBytes }
        OPTIONAL { ?ds davi-meta:fileCount ?numFiles }
        OPTIONAL { ?ds davi-meta:downloadCount ?numDownloads }
        OPTIONAL { ?ds schema:url ?url }
        OPTIONAL { ?ds schema:dateCreated ?date }

        OPTIONAL {
            ?ds davi-meta:uploader ?uploader .
            ?uploader schema:name ?uploadedBy .
            OPTIONAL { ?uploader schema:url ?uploadedByUrl }
        }
    }
    """


def build_single_dataset_query(dataset_id: str) -> str:
    return f"""
    SELECT ?ds ?id ?name ?desc ?url ?date ?sizeBytes ?numFiles ?numDownloads ?uploadedBy ?uploadedByUrl
    WHERE {{
        ?ds a davi-meta:Dataset ;
            dcterms:identifier "{dataset_id}" ;
            dcterms:identifier ?id ;
            schema:name ?name ;
            schema:description ?desc .

        OPTIONAL {{ ?ds davi-meta:sizeBytes ?sizeBytes }}
        OPTIONAL {{ ?ds davi-meta:fileCount ?numFiles }}
        OPTIONAL {{ ?ds davi-meta:downloadCount ?numDownloads }}
        OPTIONAL {{ ?ds schema:url ?url }}
        OPTIONAL {{ ?ds schema:dateCreated ?date }}

        OPTIONAL {{
            ?ds davi-meta:uploader ?uploader .
            ?uploader schema:name ?uploadedBy .
            OPTIONAL {{ ?uploader schema:url ?uploadedByUrl }}
        }}
    }}
    """


def build_dataset_views_query(dataset_uri: str) -> str:
    """
    Finds all DataViews linked to the dataset via davi-meta:hasView
    """
    return f"""
    SELECT ?view ?label ?targetClass ?icon ?desc ?example
    WHERE {{
        <{dataset_uri}> davi-meta:hasView ?view .
        ?view davi-meta:uiLabel ?label ;
              davi-meta:targetClass ?targetClass .

        OPTIONAL {{ ?targetClass davi-meta:icon ?icon }}

        OPTIONAL {{ ?view dcterms:description ?desc }}
        OPTIONAL {{ ?view davi-meta:exampleResource ?example }}
    }}
    ORDER BY ?label
    """


def build_view_config_query(view_uri: str) -> str:
    """
    Fetches Dimensions and Metrics for a specific View.

    Supports two patterns:
    1. Modular Binding (NEW): View -> ConfigNode -> Property
       Allows overriding labels/viz types per view.
    2. Direct Linking (OLD): View -> Property
       Uses global default labels.
    """
    return f"""
    SELECT ?prop ?propLabel ?type ?vizType ?aggDefault ?aggAllowed
    WHERE {{
        {{
            # ==========================================
            # 1. FETCH DIMENSIONS
            # ==========================================
            {{
                # Pattern A: Configuration Node (Binding)
                <{view_uri}> davi-meta:hasDimension ?conf .
                ?conf davi-meta:dimensionProperty ?prop .

                # Check for View-Specific Overrides
                OPTIONAL {{ ?conf davi-meta:uiLabel ?confLabel }}
                OPTIONAL {{ ?conf davi-meta:visualizationType ?confViz }}
                OPTIONAL {{ ?conf davi-meta:defaultAggregation ?confAgg }}
            }}
            UNION
            {{
                # Pattern B: Direct Link
                <{view_uri}> davi-meta:hasDimension ?prop .
                FILTER(isURI(?prop)) # Ensure it's not a blank node
            }}
            BIND("dimension" AS ?type)
        }}
        UNION
        {{
            # ==========================================
            # 2. FETCH METRICS
            # ==========================================
            {{
                # Pattern A: Configuration Node (Binding)
                <{view_uri}> davi-meta:hasMetric ?conf .
                ?conf davi-meta:dimensionProperty ?prop .

                OPTIONAL {{ ?conf davi-meta:uiLabel ?confLabel }}
                OPTIONAL {{ ?conf davi-meta:visualizationType ?confViz }}
                OPTIONAL {{ ?conf davi-meta:defaultAggregation ?confAgg }}
            }}
            UNION
            {{
                # Pattern B: Direct Link
                <{view_uri}> davi-meta:hasMetric ?prop .
                FILTER(isURI(?prop))
            }}
            BIND("metric" AS ?type)
        }}

        # ==========================================
        # 3. GLOBAL DEFAULTS & MERGING
        # ==========================================

        OPTIONAL {{ ?prop davi-meta:uiLabel ?globalLabel }}
        OPTIONAL {{ ?prop davi-meta:visualizationType ?globalViz }}
        OPTIONAL {{ ?prop davi-meta:defaultAggregation ?globalAgg }}
        OPTIONAL {{ ?prop davi-meta:allowedAggregations ?aggAllowed }}

        # PRIORITY LOGIC:
        # 1. Use View-Specific Config (?confLabel)
        # 2. Use Global Ontology Label (?globalLabel)
        # 3. Fallback to URI String
        BIND(COALESCE(?confLabel, ?globalLabel) AS ?propLabel)

        # Same logic for Visualization Type and Aggregation
        BIND(COALESCE(?confViz, ?globalViz, "Categorical") AS ?vizType)
        BIND(COALESCE(?confAgg, ?globalAgg) AS ?aggDefault)
    }}
    ORDER BY ?type ?propLabel
    """


def build_view_visualizations_query(view_uri: str) -> str:
    """
    Fetches the specific visualizations supported by this View
    """
    return f"""
    SELECT ?viz ?vizLabel ?vizDesc ?opt ?optLabel ?targetProp
    WHERE {{
        <{view_uri}> davi-meta:supportsVisualization ?viz .
        ?viz davi-meta:uiLabel ?vizLabel .
        OPTIONAL {{ ?viz dcterms:description ?vizDesc }}

        OPTIONAL {{
            ?viz davi-meta:hasOption ?opt .
            ?opt davi-meta:uiLabel ?optLabel ;
                 davi-meta:targetProperty ?targetProp .
        }}
    }}
    """


def build_neighborhood_query(resource_uri: str, target_class: Optional[str], limit: int) -> str:
    """
    Fetches the neighborhood.
    Note: We rarely restrict the neighborhood by class strictly,
    but we can order by it to show relevant nodes first.
    """
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

        OPTIONAL {{ ?s rdfs:label | schema:name | skos:prefLabel ?sLabel }}
        OPTIONAL {{ ?o rdfs:label | schema:name | skos:prefLabel ?oLabel }}

        OPTIONAL {{ ?s a ?sType }}
        OPTIONAL {{ ?o a ?oType }}
    }}
    LIMIT {limit}
    """


def build_hierarchy_query(child_property: str, root_node: Optional[str], target_class: Optional[str],
                          limit: int = 100) -> str:
    class_filter = f"?parent a <{target_class}> . ?child a <{target_class}> ." if target_class else ""

    if root_node:
        where_logic = f"""
            BIND(<{root_node}> AS ?parent)
            ?parent <{child_property}> ?child .
            {class_filter}
        """
    else:
        where_logic = f"""
            ?parent <{child_property}> ?child .
            {class_filter}
            FILTER NOT EXISTS {{ 
                ?grandparent <{child_property}> ?parent . 
                {class_filter.replace('?parent', '?grandparent').replace('?child', '?parent')} 
            }}
        """

    return f"""
    SELECT DISTINCT ?parent ?child ?parentLabel ?childLabel ?parentType ?childType
    WHERE {{
        {where_logic}
        OPTIONAL {{ ?parent rdfs:label | schema:name | skos:prefLabel ?parentLabel }}
        OPTIONAL {{ ?parent a ?parentType }}
        OPTIONAL {{ ?child rdfs:label | schema:name | skos:prefLabel ?childLabel }}
        OPTIONAL {{ ?child a ?childType }}
    }}
    LIMIT {limit}
    """


def build_view_target_class_query(view_uri: str) -> str:
    return f"""
    SELECT ?targetClass WHERE {{
        <{view_uri}> davi-meta:targetClass ?targetClass .
    }}
    """


def build_distribution_query(
    target_property: str,
    target_class: Optional[str],
    granularity: GranularityEnum,
    limit: int
) -> str:
    class_filter = f"?s a <{target_class}> ." if target_class else ""

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
        {class_filter}
        ?s <{target_property}> ?rawVal .
        FILTER(BOUND(?rawVal))
        {bind_logic}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?count)
    LIMIT {limit}
    """


def build_custom_analytics_query(
    dimension: str,
    metric: Optional[str],
    target_class: Optional[str],
    aggregation: AggregationType,
    limit: int
) -> str:
    class_filter = f"?s a <{target_class}> ." if target_class else ""

    if (dimension.startswith("http://") or dimension.startswith("https://")) and "/http" not in dimension:
        dim_pred = f"<{dimension}>"
    else:
        dim_pred = dimension

    if not metric:
        selection = "(COUNT(DISTINCT ?s) as ?val)"
        metric_pattern = ""
    else:
        if (metric.startswith("http://") or metric.startswith("https://")) and "/http" not in metric:
            met_pred = f"<{metric}>"
        else:
            met_pred = metric

        selection = f"({aggregation.value}(xsd:decimal(?metricRaw)) as ?val)"
        metric_pattern = f"?s {met_pred} ?metricRaw ."

    return f"""
    SELECT ?groupKey {selection}
    WHERE {{
        {class_filter}
        ?s {dim_pred} ?dimVal .
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

        OPTIONAL {{ ?p rdfs:label ?pLabel }}
        OPTIONAL {{ ?p schema:name ?pLabel }}
        OPTIONAL {{ ?p skos:prefLabel ?pLabel }}

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
