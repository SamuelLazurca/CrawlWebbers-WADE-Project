from collections import defaultdict

from app.core.sparql import run_sparql
from app.models.schemas import ComparisonResponse, ComparisonItem
from app.utils.sparql_queries import build_comparison_query


def compare_entities(uri_a: str, uri_b: str) -> ComparisonResponse:
    query = build_comparison_query(uri_a, uri_b)
    results = run_sparql(query)

    # Organize data into Sets for O(1) lookups
    # Structure: data_map[property_uri][value_str] = { 'A', 'B' }
    data_map = defaultdict(lambda: defaultdict(set))

    # Metadata storage to reconstruct objects later
    meta_map = {}

    for row in results:
        source = row["source"]["value"]  # "A" or "B"
        p_uri = row["p"]["value"]
        o_val = row["o"]["value"]

        p_label = row.get("pLabel", {}).get("value", p_uri.split("#")[-1].split("/")[-1])
        o_label = row.get("oLabel", {}).get("value")

        # Clean up the label if it looks like a URI
        if not o_label and "http" in o_val:
            o_label = o_val.split("#")[-1].split("/")[-1]

        data_map[p_uri][o_val].add(source)

        key = (p_uri, o_val)
        if key not in meta_map:
            meta_map[key] = {
                "property_uri": p_uri,
                "property_label": p_label,
                "value": o_val,
                "value_label": o_label
            }

    # Compute Intersection and Differences
    common = []
    unique_a = []
    unique_b = []

    for p_uri, values_dict in data_map.items():
        for val, sources in values_dict.items():
            item_meta = meta_map[(p_uri, val)]
            item_obj = ComparisonItem(**item_meta)

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
