from app.core.sparql import run_sparql
from app.models.schemas import (
    DatasetSchema, DataViewSchema, VisualizationModule,
    VisualizationOption, AnalyzableProperty
)
from app.utils.helpers import unpack_sparql_row
from app.utils.sparql_queries import (
    build_all_datasets_query,
    build_dataset_views_query,
    build_view_config_query,
    build_view_visualizations_query,
    build_single_dataset_query
)


def datasets_get_all_query() -> list[DatasetSchema]:
    results = run_sparql(build_all_datasets_query())
    datasets = []

    for row in results:
        ds_uri = unpack_sparql_row(row, "ds")

        views = _get_views_for_dataset(ds_uri)

        datasets.append(DatasetSchema(
            id=unpack_sparql_row(row, "id"),
            name=unpack_sparql_row(row, "name"),
            description=unpack_sparql_row(row, "desc"),
            url=unpack_sparql_row(row, "url"),
            added_date=unpack_sparql_row(row, "date"),
            size_in_bytes=unpack_sparql_row(row, "sizeBytes", 0, int),
            number_of_files=unpack_sparql_row(row, "numFiles", 0, int),
            number_of_downloads=unpack_sparql_row(row, "numDownloads", 0, int),
            uploaded_by=unpack_sparql_row(row, "uploadedBy"),
            uploaded_by_url=unpack_sparql_row(row, "uploadedByUrl"),
            views=views
        ))
    return datasets


def dataset_get_by_id_query(dataset_id: str) -> DatasetSchema | None:
    query = build_single_dataset_query(dataset_id)
    results = run_sparql(query)

    if not results:
        return None

    row = results[0]
    ds_uri = unpack_sparql_row(row, "ds")
    views = _get_views_for_dataset(ds_uri)

    return DatasetSchema(
        id=unpack_sparql_row(row, "id"),
        name=unpack_sparql_row(row, "name"),
        description=unpack_sparql_row(row, "desc"),
        url=unpack_sparql_row(row, "url"),
        added_date=unpack_sparql_row(row, "date"),
        size_in_bytes=unpack_sparql_row(row, "sizeBytes", 0, int),
        number_of_files=unpack_sparql_row(row, "numFiles", 0, int),
        number_of_downloads=unpack_sparql_row(row, "numDownloads", 0, int),
        uploaded_by=unpack_sparql_row(row, "uploadedBy"),
        uploaded_by_url=unpack_sparql_row(row, "uploadedByUrl"),
        views=views
    )


def _get_views_for_dataset(dataset_uri: str) -> list[DataViewSchema]:
    rows = run_sparql(build_dataset_views_query(dataset_uri))
    views = []

    for r in rows:
        view_uri = unpack_sparql_row(r, "view")

        dims, metrics = _get_view_analytics_config(view_uri)
        viz_modules = _get_view_visualizations(view_uri)

        views.append(DataViewSchema(
            id=view_uri,
            label=unpack_sparql_row(r, "label"),
            target_class=unpack_sparql_row(r, "targetClass"),
            icon=unpack_sparql_row(r, "icon", "table"),
            description=unpack_sparql_row(r, "desc"),
            example_resource=unpack_sparql_row(r, "example"),
            dimensions=dims,
            metrics=metrics,
            supported_visualizations=viz_modules
        ))
    return views


def _get_view_analytics_config(view_uri: str):
    rows = run_sparql(build_view_config_query(view_uri))
    dims_map = {}
    metrics_map = {}

    for r in rows:
        prop_uri = unpack_sparql_row(r, "prop")
        p_type = unpack_sparql_row(r, "type")

        # --- NEW LOGIC: Use Path Override if available ---
        # If sparqlPath is present (e.g. "^schema:author"), use that as the ID.
        # Otherwise, use the URI.
        path_override = unpack_sparql_row(r, "sparqlPath")
        final_id = path_override if path_override else prop_uri
        # -------------------------------------------------

        target_map = dims_map if p_type == "dimension" else metrics_map

        # Use final_id as the key to ensure we don't duplicate
        if final_id not in target_map:
            default_label = prop_uri.split("#")[-1].split("/")[-1]

            target_map[final_id] = AnalyzableProperty(
                uri=final_id,  # Frontend will now send "^schema:author" instead of the URI
                label=unpack_sparql_row(r, "propLabel", default_label),
                type=p_type,
                visualization_type=unpack_sparql_row(r, "vizType", "Categorical"),
                default_aggregation=unpack_sparql_row(r, "aggDefault", "COUNT"),
                allowed_aggregations=[]
            )

        agg_val = unpack_sparql_row(r, "aggAllowed")
        if agg_val:
            for a in agg_val.split(","):
                clean_a = a.strip()
                if clean_a not in target_map[final_id].allowed_aggregations:
                    target_map[final_id].allowed_aggregations.append(clean_a)

    return list(dims_map.values()), list(metrics_map.values())


def _get_view_visualizations(view_uri: str) -> list[VisualizationModule]:
    rows = run_sparql(build_view_visualizations_query(view_uri))
    modules_map = {}

    for r in rows:
        viz_uri = unpack_sparql_row(r, "viz")
        if viz_uri not in modules_map:
            modules_map[viz_uri] = VisualizationModule(
                id=viz_uri,
                label=unpack_sparql_row(r, "vizLabel"),
                description=unpack_sparql_row(r, "vizDesc"),
                options=[]
            )

        opt_id = unpack_sparql_row(r, "opt")
        if opt_id:
            # --- FIX: Use Path Override if available ---
            prop_uri = unpack_sparql_row(r, "targetProp")
            path_override = unpack_sparql_row(r, "sparqlPath")

            final_property = path_override if path_override else prop_uri
            # -------------------------------------------

            modules_map[viz_uri].options.append(VisualizationOption(
                id=opt_id,
                label=unpack_sparql_row(r, "optLabel"),
                target_property=final_property  # Now sends "^schema:author" to frontend
            ))

    return list(modules_map.values())
