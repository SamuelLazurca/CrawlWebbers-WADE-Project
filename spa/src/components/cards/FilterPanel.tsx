import React, {useEffect, useState} from 'react';
import type {FilterItem, FilterRequest, FilterResultItem} from '../../types';
import {FilterOperator} from '../../types';
import {parseAgentSuggestions, runFilterQuery} from '../../lib/filter';
import {Plus, Search, X} from 'lucide-react';
import {useSidebarContext} from "../../context/sidebarContext.tsx";

const DEFAULT_LIMIT = 25;

const emptyFilter = (): FilterItem => ({
  property_uri: '',
  operator: FilterOperator.CONTAINS,
  value: '',
  path_to_target: undefined,
});

interface Props {
  datasetClass: string; 
}

export const FilterPanel: React.FC<Props> = ({ datasetClass }) => {
  const [filters, setFilters] = useState<FilterItem[]>([]);
  const [intelligentMode, setIntelligentMode] = useState(false);
  const [nlInput, setNlInput] = useState('');
  const [results, setResults] = useState<FilterResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [agentLoading, setAgentLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [offset, setOffset] = useState(0);
  const {baseDataset} = useSidebarContext()

  const updateFilter = (i: number, patch: Partial<FilterItem>) => {
    setFilters(prev => prev.map((f, idx) => idx === i ? ({...f, ...patch}) : f));
  };
  const addFilter = () => setFilters(prev => [...prev, emptyFilter()]);
  const removeFilter = (i: number) => setFilters(prev => prev.filter((_, idx) => idx !== i));

  const buildRequest = (): FilterRequest => ({
    dataset_class: datasetClass,
    filters,
    limit,
    offset,
  });

  const runQuery = async () => {
    setError(null);
    setLoading(true);
    try {
      const req = buildRequest();
      const res = await runFilterQuery(req);
      setResults(res);
    } catch (err: any) {
      setError(err.message ?? String(err));
    } finally {
      setLoading(false);
    }
  };

  const askAgent = async () => {
    setError(null);
    setAgentLoading(true);
    try {
      const suggestions = await parseAgentSuggestions(nlInput, datasetClass);
      if (suggestions && suggestions.length > 0) setFilters(suggestions);
      else setError('No results');
    } catch (err: any) {
      setError(err.message ?? String(err));
    } finally {
      setAgentLoading(false);
    }
  };

  const nextPage = () => { setOffset(prev => prev + limit); };
  const prevPage = () => { setOffset(prev => Math.max(0, prev - limit)); };

  useEffect(() => {
    if (loading) return;
    void runQuery();
  }, [offset, baseDataset]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Filter</h2>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={intelligentMode} onChange={(e) => setIntelligentMode(e.target.checked)} />
            <span>Intelligent mode</span>
          </label>
          <button
            onClick={runQuery}
            className="flex items-center gap-2 px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white"
          >
            <Search size={14} /> Run
          </button>
        </div>
      </div>

      {intelligentMode ? (
        <div className="space-y-2 p-4 bg-slate-800 rounded">
          <label className="text-sm text-slate-300">Describe what you want (natural language)</label>
          <textarea
            value={nlInput}
            onChange={e => setNlInput(e.target.value)}
            rows={3}
            className="w-full bg-slate-900 p-2 rounded border border-slate-700 text-sm"
            placeholder="Ex: Find vulnerabilities mentioning log4j in applications by vendor X"
          />
          <div className="flex items-center gap-2">
            <button
              onClick={askAgent}
              disabled={agentLoading || nlInput.trim().length === 0}
              className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-white disabled:opacity-50"
            >
              {agentLoading ? 'Generating...' : 'Generate filters'}
            </button>
            <button
              onClick={() => { setFilters([emptyFilter()]); setNlInput(''); setResults([]); }}
              className="px-3 py-1 rounded border border-slate-700 text-sm"
            >
              Clear
            </button>
            <div className="text-xs text-slate-400 ml-auto">
              After generation you can edit filters and press Run.
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {filters.map((f, idx) => (
            <div key={idx} className="grid grid-cols-12 gap-2 items-center p-2 bg-slate-800 rounded">
              <input
                className="col-span-5 bg-slate-900 p-2 rounded border border-slate-700 text-sm"
                placeholder="Property URI (e.g. http://schema.org/name)"
                value={f.property_uri}
                onChange={e => updateFilter(idx, { property_uri: e.target.value })}
              />
              <select
                className="col-span-2 bg-slate-900 p-2 rounded border border-slate-700 text-sm"
                value={f.operator}
                onChange={e => updateFilter(idx, { operator: e.target.value as FilterOperator })}
              >
                <option value={FilterOperator.CONTAINS}>Contains</option>
                <option value={FilterOperator.NOT_CONTAINS}>Not contains</option>
                <option value={FilterOperator.EQUALS}>Equals</option>
                <option value={FilterOperator.NOT_EQUALS}>Not equals</option>
                <option value={FilterOperator.GT}>Greater</option>
                <option value={FilterOperator.LT}>Less</option>
                <option value={FilterOperator.TRANSITIVE}>Transitive</option>
              </select>

              <input
                className="col-span-3 bg-slate-900 p-2 rounded border border-slate-700 text-sm"
                placeholder="Value"
                value={String(f.value ?? '')}
                onChange={e => updateFilter(idx, { value: e.target.value })}
              />

              <input
                className="col-span-1 bg-slate-900 p-2 rounded border border-slate-700 text-sm"
                placeholder="path?"
                value={f.path_to_target ?? ''}
                onChange={e => updateFilter(idx, { path_to_target: e.target.value })}
              />

              <div className="col-span-1 flex gap-1 justify-end">
                <button onClick={() => removeFilter(idx)} className="p-1 rounded bg-red-600/30 hover:bg-red-600 text-xs">
                  <X size={14} />
                </button>
              </div>
            </div>
          ))}

          <div>
            <button onClick={addFilter} className="inline-flex items-center gap-2 px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-sm">
              <Plus size={14} /> Add filter
            </button>
          </div>
        </div>
      )}

      {error && <div className="text-red-400 text-sm">{error}</div>}

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Results ({results.length})</h3>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <label>Per page:</label>
            <select value={limit} onChange={(e) => { setLimit(Number(e.target.value)); setOffset(0); }} className="bg-slate-900 p-1 rounded border border-slate-700">
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>

        <div className="bg-slate-900 p-3 rounded min-h-30">
          {loading ? (
            <div className="text-sm text-slate-400">Loading...</div>
          ) : results.length === 0 ? (
            <div className="text-sm text-slate-500">No results</div>
          ) : (
            <ul className="space-y-2">
              {results.map((it) => (
                <li key={it.uri} className="p-2 rounded border border-slate-800 flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <a className="font-medium text-emerald-300 truncate" href={it.uri} target="_blank" rel="noopener noreferrer">{it.label}</a>
                      <span className="text-xs text-slate-500 truncate">{it.type}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      {Object.entries(it.matches || {}).slice(0,3).map(([k,v]) => <span key={k} className="mr-2"><strong className="text-slate-300">{k}:</strong> {v}</span>)}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="flex items-center gap-2 justify-end">
          <button onClick={prevPage} disabled={offset === 0} className="px-3 py-1 rounded border border-slate-700 disabled:opacity-50">Prev</button>
          <button onClick={nextPage} className="px-3 py-1 rounded border border-slate-700">Next</button>
        </div>
      </div>
    </div>
  );
};
