from app.core.sparql import run_sparql
from app.models.schemas import (
    DatasetSchema,
    VisualizationModule,
    VisualizationOption,
    AnalyzableProperty
)


def datasets_get_all_query() -> list[DatasetSchema]:
    # 1. Fetch the core dataset metadata
    query = """
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
    results = run_sparql(query)
    datasets = []

    for row in results:
        ds_uri = row["ds"]["value"]
        ds_id = row["id"]["value"]

        # 2. Fetch Presets (Backward Compatibility)
        viz_modules = _get_visualizations_for_dataset(ds_uri)

        # 3. Fetch PER-DATASET Dimensions and Metrics (Robust Filtering)
        dims, metrics = _get_analytics_config(ds_uri)

        datasets.append(DatasetSchema(
            id=ds_id,
            name=row["name"]["value"],
            description=row["desc"]["value"],
            url=row.get("url", {}).get("value"),
            added_date=row.get("date", {}).get("value"),
            size_in_bytes=int(row["sizeBytes"]["value"]),
            number_of_files=int(row["numFiles"]["value"]),
            number_of_downloads=int(row["numDownloads"]["value"]),
            uploaded_by=row.get("uploadedBy", {}).get("value"),
            uploaded_by_url=row.get("uploadedByUrl", {}).get("value"),
            supported_visualizations=viz_modules,
            # Attach the filtered building blocks
            dimensions=dims,
            metrics=metrics
        ))

    return datasets


def dataset_get_by_id_query(dataset_id: str) -> DatasetSchema | None:
    # We reuse the main query to ensure a consistent population of all fields
    all_ds = datasets_get_all_query()
    for ds in all_ds:
        if ds.id == dataset_id:
            return ds
    return None


def _get_visualizations_for_dataset(dataset_uri: str) -> list[VisualizationModule]:
    """
    Fetches the 'Preset' visualizations defined in datasets_ontology.ttl
    (e.g., 'Timeline', 'Severity Distribution').
    """
    query = f"""
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
    rows = run_sparql(query)

    modules_map = {}

    for r in rows:
        viz_uri = r["viz"]["value"]
        if viz_uri not in modules_map:
            modules_map[viz_uri] = VisualizationModule(
                id=viz_uri,
                label=r["vizLabel"]["value"],
                description=r.get("vizDesc", {}).get("value"),
                options=[]
            )

        if "opt" in r:
            modules_map[viz_uri].options.append(VisualizationOption(
                id=r["opt"]["value"],
                label=r["optLabel"]["value"],
                target_property=r["targetProp"]["value"]
            ))

    return list(modules_map.values())


def _get_analytics_config(dataset_uri: str) -> tuple[list[AnalyzableProperty], list[AnalyzableProperty]]:
    """
    Fetches configured Dimensions and Metrics SPECIFIC to the given dataset.
    This relies on 'davi-meta:hasDimension' and 'davi-meta:hasMetric' links in the ontology.
    """
    query = f"""
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

        # Fetch the human-readable label defined in the Domain Ontology
        OPTIONAL {{ ?prop davi-meta:uiLabel ?label }}
    }}
    ORDER BY ?label
    """
    rows = run_sparql(query)

    dimensions = []
    metrics = []

    for r in rows:
        prop_uri = r["prop"]["value"]
        prop_type = r["type"]["value"]

        # Fallback to URI fragment if label is missing
        label = r.get("label", {}).get("value", prop_uri.split("#")[-1].split("/")[-1])

        prop_obj = AnalyzableProperty(uri=prop_uri, label=label)

        if prop_type == "dimension":
            dimensions.append(prop_obj)
        elif prop_type == "metric":
            metrics.append(prop_obj)

    return dimensions, metrics
