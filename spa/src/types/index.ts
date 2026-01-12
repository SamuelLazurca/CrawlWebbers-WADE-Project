export type Result<T> =
  | { success: true; data: T; error: null }
  | { success: false; data: null; error: string };

export interface AnalyzableProperty {
  uri: string;
  label: string;
  type: 'dimension' | 'metric';
  visualization_type?: string;
  default_aggregation?: string;
  allowed_aggregations?: string[];
}

export interface VisualizationOption {
  id: string;
  label: string;
  target_property: string;
}

export interface VisualizationModule {
  id: string;
  label: string;
  description?: string;
  options: VisualizationOption[];
}

export interface DataView {
  id: string;
  label: string;
  target_class: string;
  icon: string;
  description?: string;
  example_resource?: string;

  dimensions: AnalyzableProperty[];
  metrics: AnalyzableProperty[];
  supported_visualizations: VisualizationModule[];
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  url?: string;
  size_in_bytes: number;
  number_of_files: number;
  number_of_downloads: number;
  added_date?: string;
  uploaded_by?: string;
  uploaded_by_url?: string;

  // FIX: Added this back so baseDataset.example_resource works as a fallback
  example_resource?: string;

  views: DataView[];
}

export interface ItemsResponse<T> {
  items: T[];
}

export interface Concept {
  uri: string;
  label: string;
  definition?: string;
  category: string;
  relatedCount: number;
  color: string;
}

export interface FilterFacet {
  property: string;
  values: Array<{ label: string; count: number }>;
  isExpanded?: boolean;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface TrendData {
  property: string;
  granularity: string;
  totalRecords: number;
  data: TrendPoint[];
}

// --- GRAPH TYPES ---

export interface GraphNode {
  id: string;
  label: string;
  group: string;
  value: number;
  x?: number;
  y?: number;
  z?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  weight: number;
}

export interface NeighborhoodResponse {
  center_node: string;
  nodes: GraphNode[];
  links: GraphEdge[];
}

export const FilterOperator = {
  TRANSITIVE: 'TRANSITIVE',
  CONTAINS: 'CONTAINS',
  NOT_CONTAINS: 'NOT_CONTAINS',
  EQUALS: 'EQ',
  NOT_EQUALS: 'NEQ',
  GT: 'GT',
  LT: 'LT',
} as const;

export type FilterOperator = typeof FilterOperator[keyof typeof FilterOperator];

export interface FilterItem {
  property_uri: string;
  operator: FilterOperator;
  value: string | number;
  path_to_target?: string | null;
}

export interface FilterRequest {
  target_class: string;
  filters: FilterItem[];
  limit?: number;
  offset?: number;
}

export interface FilterResultItem {
  uri: string;
  label: string;
  type?: string;
  matches?: Record<string, string>;
}

export type RechartsData = Record<string, unknown>;

export interface TooltipPayloadItem {
  name?: string;
  value?: string | number;
}

export type GraphEmptyState =
  | { kind: 'no-dataset' }
  | { kind: 'missing-start-uri' }
  | { kind: 'ready'; startUri: string };
