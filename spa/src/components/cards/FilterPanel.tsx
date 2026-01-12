import React, {useCallback, useEffect, useState} from 'react';
import type {FilterItem, FilterRequest, FilterResultItem} from '../../types';
import {FilterOperator} from '../../types';
import {parseAgentSuggestions, runFilterQuery} from '../../lib/filter';
import {Loader2, Plus, Search, Sparkles, X} from 'lucide-react';
import {useSidebarContext} from "../../context/sidebarContext";

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
  // Draft filters (UI state)
  const [filters, setFilters] = useState<FilterItem[]>([]);
  // Active filters (Query state) - Used for the useEffect dependency
  const [activeFilters, setActiveFilters] = useState<FilterItem[]>([]);

  const [intelligentMode, setIntelligentMode] = useState(false);
  const [nlInput, setNlInput] = useState('');
  const [results, setResults] = useState<FilterResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [agentLoading, setAgentLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [offset, setOffset] = useState(0);
  const { currentView } = useSidebarContext();

  // Reset when view changes
  useEffect(() => {
    setFilters([]);
    setActiveFilters([]);
    setResults([]);
    setNlInput('');
    setError(null);
    setOffset(0);
  }, [currentView]);

  const updateFilter = (i: number, patch: Partial<FilterItem>) => {
    setFilters(prev => prev.map((f, idx) => idx === i ? ({...f, ...patch}) : f));
  };

  const addFilter = () => setFilters(prev => [...prev, emptyFilter()]);

  const removeFilter = (i: number) => setFilters(prev => prev.filter((_, idx) => idx !== i));

  // Wrapped in useCallback to satisfy linter if used in effects (though we use activeFilters now)
  const executeQuery = useCallback(async (queryFilters: FilterItem[], queryOffset: number) => {
    if (queryFilters.length === 0) return;

    setError(null);
    setLoading(true);

    const req: FilterRequest = {
      target_class: datasetClass,
      filters: queryFilters,
      limit,
      offset: queryOffset,
    };

    try {
      const res = await runFilterQuery(req);
      setResults(res);
    } catch (err: unknown) {
      console.error(err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  }, [datasetClass, limit]);

  const handleRunClick = () => {
    setOffset(0); // Reset pagination on new run
    setActiveFilters(filters); // Commit draft to active
    // We don't need to call executeQuery here because the useEffect below will trigger
    // when activeFilters changes.
  };

  const askAgent = async () => {
    setError(null);
    setAgentLoading(true);
    try {
      const suggestions = await parseAgentSuggestions(nlInput, datasetClass);
      if (suggestions && suggestions.length > 0) {
        setFilters(suggestions);
        setIntelligentMode(false);
      } else {
        setError('The agent could not generate filters from your description.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError("Agent error: " + err.message);
      } else {
        setError("Agent error: Unknown error");
      }
    } finally {
      setAgentLoading(false);
    }
  };

  const nextPage = () => { setOffset(prev => prev + limit); };
  const prevPage = () => { setOffset(prev => Math.max(0, prev - limit)); };

  // Effect: Runs when Active Filters OR Pagination changes
  useEffect(() => {
    if (activeFilters.length > 0) {
      void executeQuery(activeFilters, offset);
    }
  }, [activeFilters, offset, executeQuery]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Search size={18} className="text-emerald-400"/>
          Filter {currentView?.label || 'Data'}
        </h2>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
            <input
              type="checkbox"
              checked={intelligentMode}
              onChange={(e) => setIntelligentMode(e.target.checked)}
              className="accent-emerald-500"
            />
            <span className={intelligentMode ? "text-emerald-400 font-medium" : "text-slate-400"}>
                AI Agent
            </span>
          </label>
          <button
            onClick={handleRunClick}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            Run
          </button>
        </div>
      </div>

      {intelligentMode ? (
        <div className="space-y-3 p-6 bg-slate-800/40 border border-slate-700 rounded-xl">
          <div className="flex items-center gap-2 text-emerald-400 mb-2">
            <Sparkles size={18} />
            <span className="font-semibold">Natural Language Query</span>
          </div>
          <textarea
            value={nlInput}
            onChange={e => setNlInput(e.target.value)}
            rows={3}
            className="w-full bg-slate-900 p-3 rounded-lg border border-slate-700 text-sm text-slate-200 focus:border-emerald-500 outline-none transition-colors"
            placeholder={`Example: "Find ${currentView?.label || 'items'} related to 'security' created after 2020"`}
          />
          <div className="flex items-center gap-2">
            <button
              onClick={askAgent}
              disabled={agentLoading || nlInput.trim().length === 0}
              className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white disabled:opacity-50 text-sm font-medium transition-colors flex items-center gap-2"
            >
              {agentLoading ? <Loader2 size={14} className="animate-spin"/> : <Sparkles size={14} />}
              Generate Filters
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {filters.map((f, idx) => (
            <div key={idx} className="grid grid-cols-12 gap-2 items-center p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg">
              <input
                className="col-span-12 md:col-span-4 bg-slate-900 p-2 rounded border border-slate-700 text-sm text-slate-200"
                placeholder="Property URI (e.g. schema:name)"
                value={f.property_uri}
                onChange={e => updateFilter(idx, { property_uri: e.target.value })}
              />
              <select
                className="col-span-6 md:col-span-2 bg-slate-900 p-2 rounded border border-slate-700 text-sm text-slate-200"
                value={f.operator}
                onChange={e => updateFilter(idx, { operator: e.target.value as FilterOperator })}
              >
                <option value={FilterOperator.CONTAINS}>Contains</option>
                <option value={FilterOperator.NOT_CONTAINS}>Not contains</option>
                <option value={FilterOperator.EQUALS}>Equals (=)</option>
                <option value={FilterOperator.NOT_EQUALS}>Not equals (!=)</option>
                <option value={FilterOperator.GT}>Greater {'>'}</option>
                <option value={FilterOperator.LT}>Less {'<'}</option>
                <option value={FilterOperator.TRANSITIVE}>Transitive (Tree)</option>
              </select>

              <input
                className="col-span-6 md:col-span-3 bg-slate-900 p-2 rounded border border-slate-700 text-sm text-slate-200"
                placeholder="Value"
                value={String(f.value ?? '')}
                onChange={e => updateFilter(idx, { value: e.target.value })}
              />

              <input
                className="col-span-11 md:col-span-2 bg-slate-900 p-2 rounded border border-slate-700 text-sm text-slate-200"
                placeholder="Path (Optional)"
                value={f.path_to_target ?? ''}
                onChange={e => updateFilter(idx, { path_to_target: e.target.value })}
              />

              <div className="col-span-1 flex justify-end">
                <button onClick={() => removeFilter(idx)} className="p-2 rounded bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 transition-colors">
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}

          <button onClick={addFilter} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm text-slate-300 transition-colors">
            <Plus size={16} /> Add Condition
          </button>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
          <X size={14} /> {error}
        </div>
      )}

      <div className="space-y-3 pt-4 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-slate-200">Results ({results.length})</h3>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <label>Limit:</label>
            <select
              value={limit}
              onChange={(e) => { setLimit(Number(e.target.value)); setOffset(0); }}
              className="bg-slate-900 p-1 rounded border border-slate-700 text-slate-200"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>

        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 min-h-37.5">
          {loading ? (
            <div className="flex items-center justify-center h-full py-10 text-slate-500 gap-2">
              <Loader2 className="animate-spin" /> Searching...
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-10 text-slate-600">
              <Search size={32} className="mb-2 opacity-50"/>
              <p>No results found</p>
            </div>
          ) : (
            <ul className="space-y-2">
              {results.map((it) => (
                <li key={it.uri} className="p-3 rounded-lg border border-slate-800 bg-slate-900 hover:border-slate-700 transition-colors flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <a
                        className="font-medium text-emerald-400 hover:text-emerald-300 hover:underline truncate"
                        href={it.uri}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {it.label}
                      </a>
                      {it.type && <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 truncate max-w-37.5">{it.type.split('#').pop()}</span>}
                    </div>

                    {it.matches && Object.keys(it.matches).length > 0 && (
                      <div className="text-xs text-slate-400 mt-2 grid grid-cols-1 gap-1">
                        {Object.entries(it.matches).slice(0,3).map(([k,v]) => (
                          <div key={k} className="flex gap-2">
                            <span className="font-mono text-slate-500 shrink-0">{k.split('#').pop()}:</span>
                            <span className="text-slate-300 truncate">{v}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">
                Showing {results.length} items (Offset: {offset})
            </span>
          <div className="flex items-center gap-2">
            <button onClick={prevPage} disabled={offset === 0} className="px-3 py-1.5 rounded-lg border border-slate-700 text-sm hover:bg-slate-800 disabled:opacity-50 text-slate-300">Previous</button>
            <button onClick={nextPage} disabled={results.length < limit} className="px-3 py-1.5 rounded-lg border border-slate-700 text-sm hover:bg-slate-800 disabled:opacity-50 text-slate-300">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};
