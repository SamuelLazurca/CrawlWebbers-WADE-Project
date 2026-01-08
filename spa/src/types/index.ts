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

export interface Dataset {
  id: string;
  name: string;
  description: string;
  conceptCount: number;
  lastUpdated: string;
  status: 'active' | 'processing' | 'inactive';
}
