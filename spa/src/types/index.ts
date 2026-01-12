// Common Result type for API responses
export type Result<T> =
  | { success: true; data: T; error: null }
  | { success: false; data: null; error: string };

// --- DATASET & CONFIGURATION TYPES ---

export interface VisualizationOption {
  id: string;
  label: string;
  target_property: string;
}

export interface VisualizationModule {
  id: string; // e.g., "davi-meta:viz_trends"
  label: string;
  options: VisualizationOption[];
}

export interface Dataset {
  id: string;
  name?: string;
  description?: string;
  url?: string;
  size_in_bytes?: number;
  added_date?: string;
  number_of_files?: number;
  number_of_downloads?: number;
  uploaded_by?: string;
  uploaded_by_url?: string;
  main_class?: string;
  example_resource?: string;
  dimensions: AnalyzableProperty[];
  metrics: AnalyzableProperty[];
  supported_visualizations: VisualizationModule[];
}

export interface ItemsResponse<T> {
  items: T[];
}

// --- VISUALIZATION DATA TYPES ---

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

export interface ChartData {
  label: string;
  value: number;
  percentage?: number;
  trend?: 'up' | 'down' | 'stable';
}

export interface TrendPoint {
  label: string;
  count: number;
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

export interface AnalyzableProperty {
  uri: string;
  label: string;
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

export const FilterOperator = {
  TRANSITIVE: 'TRANSITIVE',
  CONTAINS: 'CONTAINS',
  NOT_CONTAINS: 'NOT_CONTAINS',
  EQUALS: 'EQUALS',
  NOT_EQUALS: 'NOT_EQUALS',
  GT: 'GT',
  LT: 'LT',
};

export type FilterOperator = typeof FilterOperator[keyof typeof FilterOperator];

export interface FilterItem {
  property_uri: string;
  operator: FilterOperator;
  value: string | number;
  path_to_target?: string | null;
}

export interface FilterRequest {
  dataset_class: string;
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
