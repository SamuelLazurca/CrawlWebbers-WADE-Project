from enum import Enum
from typing import Generic, TypeVar, List, Optional, Union, Dict, Any

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ItemsResponseSchema(GenericModel, Generic[T]):
    items: List[T]


class VisualizationOption(BaseModel):
    id: str
    label: str
    target_property: str


class VisualizationModule(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    options: List[VisualizationOption] = []


class DatasetSchema(BaseModel):
    id: str
    name: str
    description: str
    download_url: Optional[str] = None
    date_created: Optional[str] = None
    supported_visualizations: List[VisualizationModule] = []


# --- TRENDS & ANALYTICS MODELS ---

class GranularityEnum(str, Enum):
    NONE = "none"
    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class TrendPoint(BaseModel):
    label: Union[str, float, int]
    count: int

    class Config:
        from_attributes = True


class TrendsResponse(BaseModel):
    property: str
    granularity: GranularityEnum
    total_records: int
    data: List[TrendPoint]


# --- GRAPH VISUALIZATION MODELS ---

class GraphNode(BaseModel):
    id: str
    label: str
    group: str

    # Optional metadata for sizing/coloring in UI
    value: Optional[float] = 1.0


class GraphLink(BaseModel):
    source: str
    target: str
    relationship: str

    # Optional weight for edge thickness
    weight: Optional[float] = 1.0


class GraphResponse(BaseModel):
    center_node: str
    nodes: List[GraphNode]
    links: List[GraphLink]


# --- INTELLIGENT FILTERING MODELS ---

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
    # A dict of matched properties so the UI knows why it matched
    matches: Dict[str, Any] = {}
