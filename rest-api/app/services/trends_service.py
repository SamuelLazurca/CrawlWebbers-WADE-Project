from typing import List, Optional

from fastapi import HTTPException

from app.core.sparql import run_sparql
from app.models.schemas import TrendPoint, GranularityEnum, AggregationType


def _is_safe_uri(uri: str) -> bool:
    """Basic injection check."""
    return not any(c in uri for c in [" ", ";", "{", "}", "\\", '"', "'"])


def get_distribution_query(
    target_property: str,
    granularity: GranularityEnum = GranularityEnum.NONE,
    limit: int = 100
) -> List[TrendPoint]:
    """
    **Legacy/Preset Mode:**
    Calculates simple frequency distribution (COUNT) for a single property.
    Used by the 'Preset' visualizations.
    """
    if not _is_safe_uri(target_property):
        raise HTTPException(status_code=400, detail="Invalid Property URI")

    # Handles Date Grouping logic
    bind_logic = "BIND(?rawVal as ?groupKey)"
    if granularity == GranularityEnum.YEAR:
        bind_logic = "BIND(STR(YEAR(?rawVal)) as ?groupKey)"
    elif granularity == GranularityEnum.MONTH:
        bind_logic = """
            BIND(CONCAT(STR(YEAR(?rawVal)), "-", STR(MONTH(?rawVal))) as ?groupKey)
        """
    elif granularity == GranularityEnum.DAY:
        # Use SUBSTR for ISO dates (safest cross-db method)
        bind_logic = "BIND(SUBSTR(STR(?rawVal), 1, 10) as ?groupKey)"

    query = f"""
    SELECT ?groupKey (COUNT(?s) as ?count)
    WHERE {{
        ?s <{target_property}> ?rawVal .
        FILTER(BOUND(?rawVal))

        {bind_logic}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?count)
    LIMIT {limit}
    """

    results = run_sparql(query)

    trend_data = []
    for row in results:
        label = row["groupKey"]["value"]
        try:
            count_val = int(row["count"]["value"])
        except ValueError:
            count_val = 0

        trend_data.append(TrendPoint(label=label, count=count_val))

    return trend_data


def get_custom_analytics_query(
    dimension: str,
    metric: Optional[str],
    aggregation: AggregationType,
    limit: int = 20
) -> List[TrendPoint]:
    """
    Generează un query SPARQL dinamic pentru analiză personalizată.
    - dimension: URI-ul proprietății pentru axa X (ex: nist:hasWeakness)
    - metric: URI-ul proprietății pentru axa Y (ex: nist:baseScore)
    """
    
    # Validare de securitate de bază pentru URIs
    if not _is_safe_uri(dimension):
        raise HTTPException(status_code=400, detail="Invalid Dimension URI")
    if metric and not _is_safe_uri(metric):
        raise HTTPException(status_code=400, detail="Invalid Metric URI")

    # 1. Logică pentru Selecție și Agregare
    if not metric:
        # Dacă nu avem metrică, facem frecvență (COUNT pe subiecți)
        selection = "(COUNT(DISTINCT ?s) as ?val)"
        metric_pattern = ""
    else:
        # Dacă avem metrică (ex: scor, preț), aplicăm funcția de agregare pe valorile ei
        # Folosim xsd:decimal pentru a ne asigura că operațiile matematice funcționează
        selection = f"({aggregation.value}(xsd:decimal(?metricRaw)) as ?val)"
        metric_pattern = f"?s <{metric}> ?metricRaw ."

    # 2. Logică pentru Dimensiune (Axa X)
    # Extragem valoarea dimensiunii și încercăm să îi găsim un label
    dimension_pattern = f"""
        ?s <{dimension}> ?dimVal .
        
        OPTIONAL {{ 
            ?dimVal rdfs:label | schema:name ?dimLabel 
        }}
        BIND(COALESCE(STR(?dimLabel), STR(?dimVal)) as ?groupKey)
    """

    # 3. Construcția Query-ului Final
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?groupKey {selection}
    WHERE {{
        {dimension_pattern}
        {metric_pattern}
        
        # Filtrăm valorile goale sau invalide pentru metrică dacă este cazul
        {"FILTER(BOUND(?metricRaw))" if metric else ""}
    }}
    GROUP BY ?groupKey
    ORDER BY DESC(?val)
    LIMIT {limit}
    """

    # Execuție și Procesare
    try:
        results = run_sparql(query)
        data = []
        
        for row in results:
            label = row["groupKey"]["value"]
            # Curățăm label-ul dacă este un URI lung (luăm doar ultima parte)
            if "http" in label and "/" in label:
                label = label.split("/")[-1].split("#")[-1]

            raw_val = row["val"]["value"]
            # Convertim valoarea la float sau int pentru frontend
            try:
                val = float(raw_val) if "." in str(raw_val) else int(raw_val)
            except (ValueError, TypeError):
                val = 0

            data.append(TrendPoint(label=label, count=val))
            
        return data
        
    except Exception as e:
        print(f"SPARQL Error: {str(e)}")
        print(f"Query was: {query}")
        raise HTTPException(status_code=500, detail="Error executing semantic query")