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

export interface GraphNode {
  id: string;
  label: string;
  color: string;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface ItemsResponse<T> {
  items: T[];
}

export interface TrendPoint {
  label: string;
  count: number;
}

export interface TrendData {
  property: string;
  granularity: string;
  totalRecords: number;
  data: { label: string; count: number }[];
}
