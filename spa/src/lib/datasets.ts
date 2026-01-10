import {safeFetch} from '../api/client';
import type {Dataset, ItemsResponse} from '../types';

export const getDatasets = async (): Promise<Dataset[]> => {
  const response = await safeFetch<ItemsResponse<Dataset>>('/datasets');

  if (response.success && response.data) {
    return response.data.items;
  }

  console.error('Failed to fetch datasets:', response.error);
  return [];
};
