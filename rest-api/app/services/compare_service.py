from collections import defaultdict
from typing import Optional

from app.core.sparql import run_sparql
from app.models.schemas import ComparisonResponse, ComparisonItem
from app.utils.sparql_queries import build_comparison_query, build_view_config_query


def compare_entities(uri_a: str, uri_b: str, view_id: Optional[str] = None) -> ComparisonResponse:
    query = build_comparison_query(uri_a, uri_b)
    results = run_sparql(query)

    view_labels_map = {}
    if view_id:
        view_labels_map = _get_view_label_overrides(view_id)

    data_map = defaultdict(lambda: defaultdict(set))

    prop_meta_map = {}

    val_meta_map = {}

    for row in results:
        source = row["source"]["value"]  # "A" or "B"
        p_uri = row["p"]["value"]
        o_val = row["o"]["value"]

        if p_uri in view_labels_map:
            p_label = view_labels_map[p_uri]
        else:
            p_label = row.get("pLabel", {}).get("value", p_uri.split("#")[-1].split("/")[-1])

        prop_meta_map[p_uri] = p_label

        o_label = row.get("oLabel", {}).get("value")
        if not o_label and "http" in o_val:
            o_label = o_val.split("#")[-1].split("/")[-1]

        val_meta_map[(p_uri, o_val)] = o_label

        data_map[p_uri][o_val].add(source)

    common = []
    unique_a = []
    unique_b = []

    for p_uri, values_dict in data_map.items():
        p_label_final = prop_meta_map[p_uri]

        for val, sources in values_dict.items():
            val_label_final = val_meta_map[(p_uri, val)]

            item_obj = ComparisonItem(
                property_uri=p_uri,
                property_label=p_label_final,
                value=val,
                value_label=val_label_final
            )

            if "A" in sources and "B" in sources:
                common.append(item_obj)
            elif "A" in sources:
                unique_a.append(item_obj)
            elif "B" in sources:
                unique_b.append(item_obj)

    common.sort(key=lambda x: x.property_label)
    unique_a.sort(key=lambda x: x.property_label)
    unique_b.sort(key=lambda x: x.property_label)

    return ComparisonResponse(
        entity_a=uri_a,
        entity_b=uri_b,
        common_properties=common,
        unique_to_a=unique_a,
        unique_to_b=unique_b
    )


def _get_view_label_overrides(view_id: str) -> dict:
    """
    Helper to fetch the View Config and extract just the Property -> Label mapping.
    Reuses the robust query from the previous step.
    """
    query = build_view_config_query(view_id)
    results = run_sparql(query)

    label_map = {}
    for r in results:
        p_uri = r["prop"]["value"]
        if "propLabel" in r:
            label_map[p_uri] = r["propLabel"]["value"]

    return label_map
