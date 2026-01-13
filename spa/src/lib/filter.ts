import { safePost } from '../api/client';
import type {FilterRequest, FilterResultItem} from '../types';

export async function runFilterQuery(req: FilterRequest): Promise<FilterResultItem[]> {
  const res = await safePost<FilterRequest, FilterResultItem[]>('/filter/advanced', req);
  if (!res.success) {
    throw new Error(res.error || 'Unknown error during filter query');
  }

  return res.data;
}