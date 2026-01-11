from enum import Enum
from typing import Generic, TypeVar, List, Optional, Union, Dict, Any

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ItemsResponseSchema(GenericModel, Generic[T]):
    items: List[T]


# --- DATASET & CONFIGURATION MODELS ---

class VisualizationOption(BaseModel):
    """Represents a 'Preset' option defined in the ontology."""
    id: str
    label: str
    target_property: str


class VisualizationModule(BaseModel):
    """Represents a supported extension (e.g., 'Trends', 'Graph')."""
    id: str
    label: str
    description: Optional[str] = None
    options: List[VisualizationOption] = []


class AnalyzableProperty(BaseModel):
    """
    Represents a property tagged with davi-meta:isDimension or davi-meta:isMetric.
    Used for building custom visualizations.
    """
    uri: str
    label: str


class DatasetSchema(BaseModel):
    id: str
    name: str
    url: str
    description: str
    size_in_bytes: int
    number_of_files: int
    number_of_downloads: int
    added_date: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_by_url: Optional[str] = None
    supported_visualizations: List[VisualizationModule] = []
    dimensions: List[AnalyzableProperty] = []
    metrics: List[AnalyzableProperty] = []


# --- TRENDS & ANALYTICS MODELS ---

class GranularityEnum(str, Enum):
    NONE = "none"
    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class AggregationType(str, Enum):
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MAX = "max"
    MIN = "min"


class TrendPoint(BaseModel):
    label: Union[str, float, int]
    count: Optional[float] = 0

    class Config:
        from_attributes = True


class TrendsResponse(BaseModel):
    property: str
    granularity: GranularityEnum
    total_records: Optional[float]
    data: List[TrendPoint]


# --- GRAPH VISUALIZATION MODELS ---

class GraphNode(BaseModel):
    id: str
    label: str
    group: str
    value: Optional[float] = 1.0


class GraphLink(BaseModel):
    source: str
    target: str
    relationship: str
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
    matches: Dict[str, Any] = {}


# --- COMPARE EXTENSION MODELS ---

class ComparisonItem(BaseModel):
    property_uri: str
    property_label: str
    value: str
    value_label: Optional[str] = None

class ComparisonResponse(BaseModel):
    entity_a: str
    entity_b: str
    common_properties: List[ComparisonItem] = []
    unique_to_a: List[ComparisonItem] = []
    unique_to_b: List[ComparisonItem] = []
