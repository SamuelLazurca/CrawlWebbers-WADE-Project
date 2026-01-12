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
    """
    return f"""
    PREFIX davi-meta: <https://purl.org/davi/vocab/meta#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>

    SELECT ?prop ?propLabel ?type ?vizType ?aggDefault ?aggAllowed ?sparqlPath
    WHERE {{
        {{
            # ==========================================
            # 1. FETCH DIMENSIONS
            # ==========================================
            {{
                # Pattern A: Configuration Node
                <{view_uri}> davi-meta:hasDimension ?conf .
                ?conf davi-meta:dimensionProperty ?prop .

                OPTIONAL {{ ?conf davi-meta:uiLabel ?confLabel }}
                OPTIONAL {{ ?conf davi-meta:visualizationType ?confViz }}
                OPTIONAL {{ ?conf davi-meta:defaultAggregation ?confAgg }}
                OPTIONAL {{ ?conf davi-meta:sparqlPath ?confPath }}
            }}
            UNION
            {{
                # Pattern B: Direct Link
                <{view_uri}> davi-meta:hasDimension ?prop .
                FILTER(isURI(?prop)) 
            }}
            BIND("dimension" AS ?type)
        }}
        UNION
        {{
            # ==========================================
            # 2. FETCH METRICS
            # ==========================================
            {{
                # Pattern A: Configuration Node
                <{view_uri}> davi-meta:hasMetric ?conf .
                ?conf davi-meta:dimensionProperty ?prop .

                OPTIONAL {{ ?conf davi-meta:uiLabel ?confLabel }}
                OPTIONAL {{ ?conf davi-meta:visualizationType ?confViz }}
                OPTIONAL {{ ?conf davi-meta:defaultAggregation ?confAgg }}
                OPTIONAL {{ ?conf davi-meta:sparqlPath ?confPath }}
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
        # 3. GLOBAL DEFAULTS
        # ==========================================
        OPTIONAL {{ ?prop davi-meta:uiLabel ?globalLabel }}
        OPTIONAL {{ ?prop davi-meta:visualizationType ?globalViz }}
        OPTIONAL {{ ?prop davi-meta:defaultAggregation ?globalAgg }}
        OPTIONAL {{ ?prop davi-meta:allowedAggregations ?aggAllowed }}
        OPTIONAL {{ ?prop davi-meta:sparqlPath ?globalPath }}

        # ==========================================
        # 4. RESOLUTION LOGIC
        # ==========================================

        BIND(COALESCE(?confLabel, ?globalLabel, ?rdfsLabel) AS ?propLabel)
        BIND(COALESCE(?confViz, ?globalViz, "Categorical") AS ?vizType)
        BIND(COALESCE(?confAgg, ?globalAgg, "COUNT") AS ?aggDefault)
        BIND(COALESCE(?confPath, ?globalPath) AS ?sparqlPath)
    }}
    ORDER BY ?type ?propLabel
    """


def build_view_visualizations_query(view_uri: str) -> str:
    """
    Fetches the specific visualizations supported by this View
    """
    return f"""
    PREFIX davi-meta: <https://purl.org/davi/vocab/meta#>

    SELECT ?viz ?vizLabel ?vizDesc ?opt ?optLabel ?targetProp ?sparqlPath
    WHERE {{
        <{view_uri}> davi-meta:supportsVisualization ?viz .
        ?viz davi-meta:uiLabel ?vizLabel .
        OPTIONAL {{ ?viz dcterms:description ?vizDesc }}

        OPTIONAL {{
            ?viz davi-meta:hasOption ?opt .
            ?opt davi-meta:uiLabel ?optLabel ;
                 davi-meta:targetProperty ?targetProp .

            OPTIONAL {{ ?targetProp davi-meta:sparqlPath ?sparqlPath }}
        }}
    }}
    """


def build_neighborhood_query(resource_uri: str, target_class: Optional[str], limit: int) -> str:
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

    # 1. Handle Property vs URI
    if (target_property.startswith("http://") or target_property.startswith(
            "https://")) and "/http" not in target_property:
        prop_pred = f"<{target_property}>"
    else:
        prop_pred = target_property

    # 2. Logic to detect Inverse Properties (counting incoming edges)
    # If the property path starts with ^, we Group By SUBJECT (the Entity) and Count OBJECTS (the Links).
    # Otherwise, we Group By OBJECT (the Value) and Count SUBJECTS (the Entities).
    is_inverse = target_property.strip().startswith("^")

    if is_inverse:
        # INVERSE: "Top Active Users" (Group by User ?s, Count Ratings ?rawVal)
        group_var = "?s"
        count_var = "?rawVal"
        label_target = "?s"  # We need the label of the User/Entity
    else:
        # DIRECT: "Movies by Genre" (Group by Genre ?rawVal, Count Movies ?s)
        group_var = "?rawVal"
        count_var = "?s"
        label_target = "?rawVal"  # We need the label of the Genre/Value

    # 3. Handle Granularity (Date grouping) - Only applies to ?rawVal
    if granularity == GranularityEnum.YEAR:
        bind_logic = "BIND(STR(YEAR(?rawVal)) as ?groupKey)"
    elif granularity == GranularityEnum.MONTH:
        bind_logic = """BIND(CONCAT(STR(YEAR(?rawVal)), "-", STR(MONTH(?rawVal))) as ?groupKey)"""
    elif granularity == GranularityEnum.DAY:
        bind_logic = "BIND(SUBSTR(STR(?rawVal), 1, 10) as ?groupKey)"
    else:
        # Generic Label Resolution for the Group Key
        bind_logic = f"""
        OPTIONAL {{ {label_target} rdfs:label | schema:name | skos:prefLabel ?lbl }}
        BIND(COALESCE(STR(?lbl), STR({label_target})) as ?groupKey)
        """

    return f"""
    SELECT ?groupKey (COUNT({count_var}) as ?count)
    WHERE {{
        {class_filter}
        ?s {prop_pred} ?rawVal . 
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

    # 1. Wrapper Logic (Handle raw URIs vs Paths)
    if (dimension.startswith("http://") or dimension.startswith("https://")) and "/http" not in dimension:
        dim_pred = f"<{dimension}>"
    else:
        dim_pred = dimension

    # 2. Detect Inverse Property (e.g. ^schema:author)
    is_inverse = dimension.strip().startswith("^")

    if is_inverse:
        # INVERSE: Group by the Entity (?s), Count the Links (?dimVal)
        # Example: "Active Users" -> Group by User, Count Ratings
        group_node = "?s"
        count_node = "?dimVal"
    else:
        # NORMAL: Group by the Value (?dimVal), Count the Entities (?s)
        # Example: "Movies by Genre" -> Group by Genre, Count Movies
        group_node = "?dimVal"
        count_node = "?s"

    # 3. Handle Metric / Aggregation
    if not metric:
        # Default: Frequency Count
        selection = f"(COUNT(DISTINCT {count_node}) as ?val)"
        metric_pattern = ""
    else:
        # If Metric exists, wrap it properly
        if (metric.startswith("http://") or metric.startswith("https://")) and "/http" not in metric:
            met_pred = f"<{metric}>"
        else:
            met_pred = metric

        selection = f"({aggregation.value}(xsd:decimal(?metricRaw)) as ?val)"
        # Metrics usually apply to the main Subject (?s)
        metric_pattern = f"?s {met_pred} ?metricRaw ."

    return f"""
    SELECT ?groupKey {selection}
    WHERE {{
        {class_filter}
        ?s {dim_pred} ?dimVal .

        # Dynamic Label Resolution for the Group Key
        OPTIONAL {{ {group_node} rdfs:label | schema:name | skos:prefLabel ?lbl }}
        BIND(COALESCE(STR(?lbl), STR({group_node})) as ?groupKey)

        {metric_pattern}
        {"FILTER(BOUND(?metricRaw))" if metric else ""}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?val)
    LIMIT {limit}
    """


def build_comparison_query(uri_a: str, uri_b: str, limit: int = 500) -> str:
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
