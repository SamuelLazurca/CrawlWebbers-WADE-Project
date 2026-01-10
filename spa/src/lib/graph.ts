import {safeFetch} from '../api/client';
import type {NeighborhoodResponse} from '../types';

export const getGraphData = async (startUri: string): Promise<NeighborhoodResponse> => {
  const url = `/graph/neighborhood?resource_uri=${encodeURIComponent(startUri)}`;
  const response = await safeFetch<NeighborhoodResponse>(url);

  if (response.success && response.data) {
    return response.data;
  }

  console.error('Failed to fetch graph data:', response.error);
  return {
    center_node: startUri,
    nodes: [],
    links: []
  };
};
