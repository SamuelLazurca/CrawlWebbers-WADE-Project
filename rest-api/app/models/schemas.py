from enum import Enum
from typing import Generic, TypeVar, List, Optional, Union, Dict, Any

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

T = TypeVar("T")


class ItemsResponseSchema(BaseModel, Generic[T]):
    items: List[T]


# --- CONFIGURATION MODELS ---

class VisualizationOption(BaseModel):
    id: str
    label: str
    target_property: str


class VisualizationModule(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    options: List[VisualizationOption] = []


class AnalyzableProperty(BaseModel):
    """
    Enhanced to support the new Ontology metadata
    """
    uri: str
    label: str
    type: str # 'dimension' or 'metric'
    # New UI hints
    visualization_type: Optional[str] = "Categorical" # e.g. Temporal, Text
    default_aggregation: Optional[str] = "COUNT"
    allowed_aggregations: List[str] = []


class DataViewSchema(BaseModel):
    """
    NEW: Represents a specific perspective (e.g., 'Movies' vs. 'Ratings')
    """
    id: str
    label: str
    target_class: str
    icon: Optional[str] = "table"  # e.g. 'film', 'bug'
    description: Optional[str] = None
    example_resource: Optional[str] = None

    # The config now lives here, inside the View
    dimensions: List[AnalyzableProperty] = []
    metrics: List[AnalyzableProperty] = []
    supported_visualizations: List[VisualizationModule] = []


class DatasetSchema(BaseModel):
    id: str
    name: str
    url: str
    description: str

    # Metadata
    size_in_bytes: int
    number_of_files: int
    number_of_downloads: int
    added_date: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_by_url: Optional[str] = None

    # A dataset now contains multiple views
    views: List[DataViewSchema] = []


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
    value: Optional[float] = 0

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
    EQUALS = "EQ"
    NOT_EQUALS = "NEQ"
    GT = "GT"
    LT = "LT"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    TRANSITIVE = "TRANSITIVE"


class FilterCondition(BaseModel):
    property_uri: str
    operator: FilterOperator
    value: Union[str, int, float]
    path_to_target: Optional[str] = None


class FilterRequest(BaseModel):
    target_class: str
    filters: List[FilterCondition]
    limit: int = 50
    offset: int = 0

class FilterResultItem(BaseModel):
    uri: str
    label: str
    type: Optional[str] = None
    matches: Dict[str, Any] = {}

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