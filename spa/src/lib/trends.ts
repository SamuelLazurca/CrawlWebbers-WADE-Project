import {safeFetch} from '../api/client';
import type {TrendData} from '../types';

export const getTrendData = async (
  propertyUri: string,
  viewId?: string,
  granularity: string = 'year'
): Promise<TrendData> => {
  const viewParam = viewId ? `&view_id=${encodeURIComponent(viewId)}` : '';
  const url = `/trends/distribution?target_property=${encodeURIComponent(propertyUri)}${viewParam}&granularity=${granularity}&limit=10`;

  const response = await safeFetch<TrendData>(url);

  if (response.success && response.data) {
    return response.data;
  }

  return {
    property: propertyUri,
    granularity,
    totalRecords: 0,
    data: []
  };
};
