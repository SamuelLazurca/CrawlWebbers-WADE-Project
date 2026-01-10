import type { TrendData, TrendPoint } from '../types';
import { safeFetch } from '../api/client';

export const getCustomAnalytics = async (
  dimension: string,
  metric: string | null,
  aggregation: string = 'COUNT',
  limit: number = 20
): Promise<TrendPoint[]> => {
  try {
    const response = await safeFetch<TrendData>(`/trends/custom?dimension=${encodeURIComponent(dimension)}&metric=${encodeURIComponent(metric || '')}&aggregation=${encodeURIComponent(aggregation.toLowerCase())}&limit=${limit}`);
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