from app.core.sparql import run_sparql
from app.models.schemas import (
    DatasetSchema, VisualizationModule, VisualizationOption, AnalyzableProperty
)
from app.utils.sparql_queries import (
    build_all_datasets_query,
    build_viz_config_query,
    build_analytics_config_query
)


def datasets_get_all_query() -> list[DatasetSchema]:
    # 1. Fetch core metadata using the imported query builder
    query = build_all_datasets_query()
    results = run_sparql(query)

    datasets = []
    for row in results:
        ds_uri = row["ds"]["value"]
        ds_id = row["id"]["value"]

        # 2. Fetch Nested Configs
        viz_modules = _get_visualizations_for_dataset(ds_uri)
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
            dimensions=dims,
            metrics=metrics
        ))
    return datasets


def dataset_get_by_id_query(dataset_id: str) -> DatasetSchema | None:
    all_ds = datasets_get_all_query()
    for ds in all_ds:
        if ds.id == dataset_id:
            return ds
    return None


def _get_visualizations_for_dataset(dataset_uri: str) -> list[VisualizationModule]:
    query = build_viz_config_query(dataset_uri)
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
    query = build_analytics_config_query(dataset_uri)
    rows = run_sparql(query)

    dimensions = []
    metrics = []
    for r in rows:
        prop_uri = r["prop"]["value"]
        prop_type = r["type"]["value"]
        label = r.get("label", {}).get("value", prop_uri.split("#")[-1].split("/")[-1])
        prop_obj = AnalyzableProperty(uri=prop_uri, label=label)

        if prop_type == "dimension":
            dimensions.append(prop_obj)
        elif prop_type == "metric":
            metrics.append(prop_obj)

    return dimensions, metrics
