import json
import logging
import os
from fastapi import APIRouter, HTTPException, Body
from typing import List
from pydantic import TypeAdapter
from strands.models.openai import OpenAIModel
from fastapi.responses import StreamingResponse
from strands import Agent
from app.agent.filters_agent import _build_agent_prompt, _extract_first_json_block, _is_safe_uri
from app.core.config import GOOGLE_API_KEY
from app.models.schemas import AgentFilterItem, AgentRequest, AgentResponse, FilterRequest, FilterResultItem
from app.services.filter_service import build_intelligent_query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/advanced", response_model=List[FilterResultItem])
def intelligent_search(
    request: FilterRequest = Body(..., description="Define facets, ranges, and semantic inference rules.")
):
    """
    **Intelligent Filtering Extension**

    Perform multi-faceted semantic search leveraging ontology hierarchy, graph traversal, and inverse relations.

    **View Context:**
    This endpoint works in the context of a specific **Data View**.
    The `target_class` parameter should match the `target_class` of the View you are querying
    (e.g., `https://purl.org/davi/vocab/nist#Vulnerability`).

    **Supported Operators:**
    - Comparison: `=`, `!=`, `>`, `<`
    - String: `CONTAINS`, `NOT_CONTAINS` (Case-insensitive)
    - Semantic: `TRANSITIVE` (Finds all children of a concept using `skos:broader` or `rdfs:subClassOf`)
    """
    try:
        return build_intelligent_query(request)
    except Exception as e:
        # Log the full error in production, return a simple message to the client
        raise HTTPException(status_code=500, detail=f"SPARQL Generation Error: {str(e)}")


@router.post("/agent", response_model=List[FilterResultItem])
async def agent_parse(req: AgentRequest = Body(...)):
    if req.dataset_class and not _is_safe_uri(req.dataset_class):
        raise HTTPException(status_code=400, detail="Invalid dataset_class URI")

    prompt = _build_agent_prompt(req.text, req.dataset_class)

    api_key = GOOGLE_API_KEY

    if not api_key:
        raise ValueError("Lipsește cheia API! Adaug-o în .env ca GOOGLE_API_KEY=...")

    model = OpenAIModel(
        client_args={
                "api_key": api_key,
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            },
            model_id="gemini-2.5-flash", 
            params={
                "max_tokens": 1000,
                "temperature": 0.7,
            }
        )

    agent = Agent(model=model)

    try:
        raw = agent(prompt)  
        print("start raw")
        print(raw)
        print("end raw")
        logger.debug("Agent raw response: %s", raw)
    except Exception as e:
        logger.exception("Agent invocation failed")
        raise HTTPException(status_code=500, detail="Agent call failed")

    json_block = _extract_first_json_block(raw)
    if not json_block:
        raise HTTPException(status_code=502, detail="Agent did not return JSON")

    try:
        parsed = json.loads(json_block)
    except Exception as e:
        logger.exception("Invalid JSON from agent")
        raise HTTPException(status_code=502, detail="Invalid JSON from agent")

    suggestions: List[AgentFilterItem] = []
    for item in parsed:
        try:
            filt = AgentFilterItem(**item)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid filter item shape: {item}")

        if filt.property_uri and filt.property_uri.startswith("http") and not _is_safe_uri(filt.property_uri):
            raise HTTPException(status_code=400, detail=f"Unsafe property_uri: {filt.property_uri}")
        if filt.path_to_target and filt.path_to_target.startswith("http") and not _is_safe_uri(filt.path_to_target):
            raise HTTPException(status_code=400, detail=f"Unsafe path_to_target: {filt.path_to_target}")

        suggestions.append(filt)

    return AgentResponse(suggestions=suggestions)
