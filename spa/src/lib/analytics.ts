import type {TrendData, TrendPoint} from '../types';
import {safeFetch} from '../api/client';

export const getCustomAnalytics = async (
  dimension: string,
  metric: string | null,
  viewId?: string,
  aggregation: string = 'COUNT',
  limit: number = 20
): Promise<TrendPoint[]> => {
  try {
    const viewParam = viewId ? `&view_id=${encodeURIComponent(viewId)}` : '';
    const url = `/trends/custom?dimension=${encodeURIComponent(dimension)}&metric=${encodeURIComponent(metric || '')}${viewParam}&aggregation=${encodeURIComponent(aggregation.toLowerCase())}&limit=${limit}`;

    const response = await safeFetch<TrendData>(url);
    if (response.success && response.data) {
      return response.data.data;
    }

    console.error("Failed to fetch custom analytics:", response.error);
    return [];
  } catch (error) {
    console.error("Error fetching custom analytics:", error);
    return [];
  }
};
