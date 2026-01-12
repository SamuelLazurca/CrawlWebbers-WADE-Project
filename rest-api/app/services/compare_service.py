from collections import defaultdict
from typing import Optional

from app.core.sparql import run_sparql
from app.models.schemas import ComparisonResponse, ComparisonItem
from app.utils.sparql_queries import build_comparison_query, build_view_config_query


def compare_entities(uri_a: str, uri_b: str, view_id: Optional[str] = None) -> ComparisonResponse:
    # 1. Fetch the raw comparison data (Generic)
    query = build_comparison_query(uri_a, uri_b)
    results = run_sparql(query)

    # 2. (Optional) Fetch View-Specific Labels to override defaults
    view_labels_map = {}
    if view_id:
        view_labels_map = _get_view_label_overrides(view_id)

    # 3. Organize data
    # Structure: data_map[property_uri][value_str] = { 'A', 'B' }
    data_map = defaultdict(lambda: defaultdict(set))

    # Metadata map to store the "Best Available Label" for each property
    prop_meta_map = {}

    # Value metadata map
    val_meta_map = {}

    for row in results:
        source = row["source"]["value"]  # "A" or "B"
        p_uri = row["p"]["value"]
        o_val = row["o"]["value"]

        # LABEL PRIORITY LOGIC:
        # 1. View-Specific Override (from view_id)
        # 2. SPARQL Label (rdfs:label, etc.)
        # 3. URI Fragment

        if p_uri in view_labels_map:
            p_label = view_labels_map[p_uri]
        else:
            p_label = row.get("pLabel", {}).get("value", p_uri.split("#")[-1].split("/")[-1])

        # Store the best label found for this property
        prop_meta_map[p_uri] = p_label

        o_label = row.get("oLabel", {}).get("value")
        # Clean up the object label if it looks like a URI
        if not o_label and "http" in o_val:
            o_label = o_val.split("#")[-1].split("/")[-1]

        # Store value metadata
        val_meta_map[(p_uri, o_val)] = o_label

        data_map[p_uri][o_val].add(source)

    # 4. Compute Intersection and Differences
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

    # Sort by the final resolved labels
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
        # The query returns 'propLabel' which is already coalesced
        # (View Override > Global Label > URI)
        if "propLabel" in r:
            label_map[p_uri] = r["propLabel"]["value"]

    return label_map
