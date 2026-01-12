import {safeFetch} from '../api/client';
import type {NeighborhoodResponse} from '../types';

export const getGraphData = async (
  startUri: string,
  viewId?: string
): Promise<NeighborhoodResponse> => {
  const viewParam = viewId ? `&view_id=${encodeURIComponent(viewId)}` : '';
  const url = `/graph/neighborhood?resource_uri=${encodeURIComponent(startUri)}${viewParam}`;

  const response = await safeFetch<NeighborhoodResponse>(url);

  if (response.success && response.data) {
    return response.data;
  }

  return {
    center_node: startUri,
    nodes: [],
    links: []
  };
};
