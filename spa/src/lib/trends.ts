import { safeFetch} from '../api/client';
import type { TrendData } from '../types';

export const getTrendData = async (propertyUri: string, granularity: string = 'year'): Promise<TrendData> => {
  const response = await safeFetch<TrendData>(`/trends/distribution?target_property=${encodeURIComponent(propertyUri)}&granularity=${granularity}&limit=10`);
    if (response.success && response.data) {
        return response.data;
    } else {
        console.error('Failed to fetch trend data:', response.error);
        return {
          property: propertyUri,
          granularity,
          totalRecords: 0,
          data: []
        };
    }
};