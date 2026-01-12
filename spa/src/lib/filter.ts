import type {FilterItem, FilterRequest, FilterResultItem} from '../types';

// Use the environment variable if available, otherwise default
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function runFilterQuery(req: FilterRequest): Promise<FilterResultItem[]> {
  const res = await fetch(`${API_BASE}/filter/advanced`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const txt = await res.text();
    let errorMsg = `Server error: ${res.status}`;

    // Try to parse JSON error for detail, but do it safely
    try {
      const jsonErr = JSON.parse(txt);
      if (jsonErr && typeof jsonErr === 'object' && 'detail' in jsonErr) {
        errorMsg = jsonErr.detail;
      }
    } catch {
      // If JSON parse fails, append the raw text if it's not too long
      if (txt && txt.length < 200) errorMsg += ` ${txt}`;
    }

    throw new Error(errorMsg);
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