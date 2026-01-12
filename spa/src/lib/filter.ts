import type {FilterItem, FilterRequest, FilterResultItem} from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

export async function runFilterQuery(req: FilterRequest): Promise<FilterResultItem[]> {
  const res = await fetch(`${API_BASE}/filter/advanced`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Server error: ${res.status} ${txt}`);
  }
  return res.json();
}

export async function parseAgentSuggestions(naturalText: string, datasetClass?: string): Promise<FilterItem[]> {
  const res = await fetch(`${API_BASE}/agent/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: naturalText, dataset_class: datasetClass }),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Agent error: ${res.status} ${txt}`);
  }
  return res.json();
}
