from app.core.sparql import run_sparql
from app.models.schemas import DatasetSchema, VisualizationModule, VisualizationOption


def datasets_get_all_query() -> list[DatasetSchema]:
    query = """
    SELECT ?ds ?id ?name ?desc ?url ?date
    WHERE {
        ?ds a davi-meta:Dataset ;
            dcterms:identifier ?id ;
            schema:name ?name ;
            schema:description ?desc .
        OPTIONAL { ?ds schema:url ?url }
        OPTIONAL { ?ds schema:dateCreated ?date }
    }
    """
    results = run_sparql(query)
    datasets = []

    for row in results:
        ds_uri = row["ds"]["value"]
        ds_id = row["id"]["value"]

        viz_modules = _get_visualizations_for_dataset(ds_uri)

        datasets.append(DatasetSchema(
            id=ds_id,
            name=row["name"]["value"],
            description=row["desc"]["value"],
            download_url=row.get("url", {}).get("value"),
            date_created=row.get("date", {}).get("value"),
            supported_visualizations=viz_modules
        ))

    return datasets


def dataset_get_by_id_query(dataset_id: str) -> DatasetSchema | None:
    # ... implementation similar to above, filtering by ?id ...
    # For brevity, reusing the getAll logic, but in production optimize this.
    all_ds = datasets_get_all_query()
    for ds in all_ds:
        if ds.id == dataset_id:
            return ds
    return None


def _get_visualizations_for_dataset(dataset_uri: str) -> list[VisualizationModule]:
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
