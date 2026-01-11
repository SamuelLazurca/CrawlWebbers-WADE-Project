import re
import logging
from typing import Any, List, List, Optional, AsyncIterator
from fastapi.responses import StreamingResponse

from strands import Agent, tool, tool

from app.models.schemas import FilterRequest, FilterResultItem
from app.services.filter_service import build_intelligent_query  

logger = logging.getLogger(__name__)

def _is_safe_uri(u: str) -> bool:
    if not u or not isinstance(u, str):
        return False
    return u.startswith("http://") or u.startswith("https://")

def _extract_first_json_block(text: str) -> Optional[str]:
    arr_match = re.search(r"(\[.*\])", text, flags=re.S)
    if arr_match:
        return arr_match.group(1)
    obj_match = re.search(r"(\{.*\})", text, flags=re.S)
    if obj_match:
        return obj_match.group(1)
    return None

SYSTEM_INSTRUCTIONS = """
You are an assistant that converts natural language filter requests into a strict JSON array.
Output must be **only valid JSON** with the following shape (array):
[
  {
    "property_uri": "http://example.org/property",
    "operator": "CONTAINS" | "EQUALS" | "NOT_CONTAINS" | "NOT_EQUALS" | "GT" | "LT" | "TRANSITIVE",
    "value": "<string or number or http-uri>",
    "path_to_target": "<optional http-uri or null>"
  },
  ...
]

Rules:
- DO NOT output explanation text, do not wrap the JSON in backticks.
- property_uri and path_to_target must be full URIs (http/https) when they refer to ontology URIs; otherwise a literal string is ok.
- Keep output concise and valid JSON only.
- Use the operator TRANSITIVE if the user means "include subclasses / hierarchical relations" (semantic transitive).
- If dataset_class is provided, prefer properties relevant to that class if you can infer them.
"""

def _build_agent_prompt(nl_text: str, dataset_class: Optional[str]) -> str:
    extra = f"Dataset class: {dataset_class}\n\n" if dataset_class else ""
    examples = """
Examples (output only JSON):

User: "Find vulns mentioning log4j from vendor Apache"
Output:
[
  {"property_uri": "http://schema.org/name", "operator": "CONTAINS", "value": "log4j"},
  {"property_uri": "http://example.org/hasVendor", "operator": "EQUALS", "value": "Apache"}
]

User: "Vulnerabilities under weakness category CVE-2021 or related"
Output:
[
  {"property_uri": "http://example.org/hasWeakness", "operator": "TRANSITIVE", "value": "http://example.org/CVE-2021"}
]
"""
    return SYSTEM_INSTRUCTIONS + "\n" + extra + "User request: " + nl_text + "\n\n" + examples
