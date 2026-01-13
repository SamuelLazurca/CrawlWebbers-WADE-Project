import {safePost} from '../api/client';
import type {FilterItem, FilterRequest, FilterResultItem} from '../types';


function castFilterValue(value: string | number): string | number {
  if (typeof value !== 'string') {
    return value;
  }

  const trimmed = value.trim();
  if (trimmed === '') {
    return value;
  }

  // Strict numeric check (int or float, positive or negative)
  const numericPattern = /^-?\d+(\.\d+)?$/;
  if (!numericPattern.test(trimmed)) {
    return value;
  }

  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : value;
}


export async function runFilterQuery(
  req: FilterRequest
): Promise<FilterResultItem[]> {

  const normalizedReq: FilterRequest = {
    ...req,
    filters: req.filters.map((filter: FilterItem) => ({
      ...filter,
      value: castFilterValue(filter.value),
    })),
  };

  const res = await safePost<FilterRequest, FilterResultItem[]>(
    '/filter/advanced',
    normalizedReq
  );

  if (!res.success) {
    throw new Error(res.error || 'Unknown error during filter query');
  }

  return res.data;
}
