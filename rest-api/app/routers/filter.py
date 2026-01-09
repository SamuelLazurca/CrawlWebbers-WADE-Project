from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.models.schemas import FilterRequest, FilterResultItem
from app.services.filter_service import build_intelligent_query

router = APIRouter()


@router.post("/advanced", response_model=List[FilterResultItem])
def intelligent_search(
        request: FilterRequest = Body(..., description="Define facets, ranges, and semantic inference rules.")
):
    """
    **Intelligent Filtering Extension**

    Perform multi-faceted semantic search leveraging ontology hierarchy, graph traversal, and inverse relations.

    **Supported Operators:**
    - Comparison: `=`, `!=`, `>`, `<`
    - String: `CONTAINS`, `NOT_CONTAINS` (Case-insensitive)
    - Semantic: `TRANSITIVE` (Finds all children of a concept using `skos:broader` or `rdfs:subClassOf`)

    **Advanced Capabilities & Examples:**

    1. **Inverse Relations (Finding Movies by Rating):**
       Since Ratings point TO Movies, use `^` to traverse backwards.
       * "Find movies with a rating > 4.5"
       - Class: `http://schema.org/Movie`
       - Property: `^http://schema.org/itemReviewed` (Note the `^`)
       - Path: `http://schema.org/ratingValue`
       - Operator: `>`
       - Value: `4.5`

    2. **Transitive Inference (NIST Hierarchy):**
       Find all vulnerabilities related to 'Improper Input Validation', including specific subtypes like SQLi or XSS.
       - Operator: `TRANSITIVE`
       - Value: `http://cwe.mitre.org/.../ID`

    3. **Graph Traversal (NIST Vendors):**
       Find Vulnerabilities affecting 'Adobe' products (hops from Vuln -> Software -> Vendor).
       - Property: `affectsSoftware`
       - Path: `manufacturer`
       - Operator: `CONTAINS`
       - Value: `Adobe`

    4. **Negation (Exclusion):**
       Find Action movies that are NOT Romance.
       - Property: `http://schema.org/genre`
       - Operator: `!=` (or `NOT_CONTAINS`)
       - Value: `.../genres=romance`

    5. **Date Filtering:**
       Inputs matching `YYYY-MM-DD` are automatically cast to `xsd:dateTime`.
       - Property: `datePublished`
       - Operator: `>`
       - Value: `2023-01-01`
    """
    try:
        return build_intelligent_query(request)
    except Exception as e:
        # In dev, return the error. In prod, log it.
        raise HTTPException(status_code=500, detail=f"SPARQL Generation Error: {str(e)}")
