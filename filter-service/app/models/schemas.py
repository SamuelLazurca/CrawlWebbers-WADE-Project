from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class FilterOperator(str, Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    GT = ">"
    LT = "<"
    TRANSITIVE = "TRANSITIVE"


class FilterCondition(BaseModel):
    property_uri: str
    operator: FilterOperator
    value: Union[str, int, float]
    path_to_target: Optional[str] = None


class FilterRequest(BaseModel):
    dataset_class: str
    filters: List[FilterCondition]
    limit: int = 50
    offset: int = 0


class FilterResultItem(BaseModel):
    uri: str
    label: str
    type: Optional[str] = None
    matches: Dict[str, Any] = {}
