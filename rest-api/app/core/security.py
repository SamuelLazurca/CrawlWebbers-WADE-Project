from typing import List, Optional
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
import secrets

from app.core.config import API_KEY

API_KEY_HEADER_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

def get_allowed_api_keys() -> List[str]:
    raw = API_KEY
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]

async def get_api_key(api_key_header_value: Optional[str] = Depends(api_key_header)):
    if not api_key_header_value:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Missing API key")
    allowed = get_allowed_api_keys()
    for ak in allowed:
        if secrets.compare_digest(api_key_header_value, ak):
            return api_key_header_value
    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
