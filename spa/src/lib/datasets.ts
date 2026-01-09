import { safeFetch} from '../api/client';
import type { ItemsResponse } from '../types';
import type { Dataset } from '../types/datasets';

export const getDatasets = async (): Promise<Dataset[]> => {
  const response = await safeFetch<ItemsResponse<Dataset>>('/datasets');
    if (response.success && response.data) {
        return response.data.items;
    } else {
        console.error('Failed to fetch datasets:', response.error);
        return [];
    }
}