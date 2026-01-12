import React, { useEffect, useState } from 'react';
import { ChevronDown, Database, LayoutTemplate } from 'lucide-react';
import { getDatasets } from '../lib/datasets';
import { useSidebarContext } from '../context/sidebarContext';
import { cn, formatDate, formatSize } from '../lib/utils';
import type { Dataset } from '../types';

export const DatasetSelector: React.FC = () => {
  const { baseDataset, currentView, setBaseDataset, setCurrentView } = useSidebarContext();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isDatasetOpen, setIsDatasetOpen] = useState(false);
  const [isViewOpen, setIsViewOpen] = useState(false);

  useEffect(() => {
    async function load() {
      const data = await getDatasets();
      setDatasets(data || []);
      // Auto-select first if none selected
      if (!baseDataset && data && data.length > 0) {
        setBaseDataset(data[0]);
      }
    }
    void load();
  }, []); // Run once on mount

  if (!baseDataset && datasets.length === 0) {
    return (
      <div className="p-4 border-b border-slate-800">
        <div className="text-slate-400 text-sm animate-pulse">Loading datasets...</div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 border-b border-slate-800">

      {/* --- DATASET SELECTOR --- */}
      <div className="space-y-1">
        <label className="text-[10px] uppercase tracking-wider font-bold text-slate-500 ml-1">Dataset</label>
        <div className="relative">
          <button
            onClick={() => { setIsDatasetOpen(!isDatasetOpen); setIsViewOpen(false); }}
            className={cn(
              "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all",
              "bg-slate-800/50 border border-slate-700 text-slate-200",
              "hover:border-emerald-400/50 hover:shadow-lg hover:shadow-emerald-900/10",
              isDatasetOpen && "border-emerald-400 ring-1 ring-emerald-400/20"
            )}
          >
            <div className="flex items-center gap-2 min-w-0">
              <Database size={14} className="text-cyan-400 shrink-0" />
              <span className="font-medium text-sm truncate">
                {baseDataset?.name ?? 'Select a dataset'}
              </span>
            </div>
            <ChevronDown size={14} className={cn('transition-transform duration-200 text-slate-400', isDatasetOpen && 'rotate-180')} />
          </button>

          {isDatasetOpen && (
            <div className="absolute z-50 mt-1 w-full rounded-xl bg-slate-900 border border-slate-700 shadow-xl overflow-hidden max-h-60 overflow-y-auto">
              {datasets.map((ds) => (
                <button
                  key={ds.id}
                  onClick={() => {
                    setBaseDataset(ds);
                    setIsDatasetOpen(false);
                  }}
                  className={cn(
                    'w-full text-left px-4 py-2 text-xs truncate transition border-l-2 border-transparent',
                    'hover:bg-slate-800',
                    ds.id === baseDataset?.id
                      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500'
                      : 'text-slate-300'
                  )}
                >
                  {ds.name || 'Untitled'}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* --- VIEW SELECTOR --- */}
      {baseDataset && (
        <div className="space-y-1 animate-in fade-in slide-in-from-top-2 duration-300">
          <label className="text-[10px] uppercase tracking-wider font-bold text-slate-500 ml-1">Data View</label>
          <div className="relative">
            <button
              onClick={() => { setIsViewOpen(!isViewOpen); setIsDatasetOpen(false); }}
              disabled={!baseDataset.views || baseDataset.views.length === 0}
              className={cn(
                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all",
                "bg-slate-800/30 border border-slate-700 text-slate-200",
                "hover:bg-slate-800 hover:border-emerald-400/50",
                isViewOpen && "border-emerald-400 ring-1 ring-emerald-400/20",
                (!baseDataset.views || baseDataset.views.length === 0) && "opacity-50 cursor-not-allowed"
              )}
            >
              <div className="flex items-center gap-2 min-w-0">
                <LayoutTemplate size={14} className="text-emerald-400 shrink-0" />
                <span className="font-medium text-sm truncate">
                  {currentView?.label ?? 'Select a view'}
                </span>
              </div>
              <ChevronDown size={14} className={cn('transition-transform duration-200 text-slate-400', isViewOpen && 'rotate-180')} />
            </button>

            {isViewOpen && baseDataset.views && (
              <div className="absolute z-50 mt-1 w-full rounded-xl bg-slate-900 border border-slate-700 shadow-xl overflow-hidden max-h-60 overflow-y-auto">
                {baseDataset.views.map((view) => (
                  <button
                    key={view.id}
                    onClick={() => {
                      setCurrentView(view);
                      setIsViewOpen(false);
                    }}
                    className={cn(
                      'w-full text-left px-4 py-2 text-xs truncate transition border-l-2 border-transparent',
                      'hover:bg-slate-800',
                      view.id === currentView?.id
                        ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500'
                        : 'text-slate-300'
                    )}
                  >
                    {view.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* --- METADATA --- */}
      {baseDataset && (
        <div className="pt-2">
          {baseDataset.description && (
            <p className="text-xs text-slate-400 italic line-clamp-2 mb-3 px-1">
              {baseDataset.description}
            </p>
          )}
          <div className="grid grid-cols-2 gap-2 text-[10px] px-1 bg-slate-800/30 p-2 rounded-lg border border-slate-800">
            <DatasetMeta label="Files" value={baseDataset.number_of_files} highlight />
            <DatasetMeta label="Downloads" value={baseDataset.number_of_downloads} highlight />
            <DatasetMeta label="Size" value={formatSize(baseDataset.size_in_bytes)} />
            <DatasetMeta label="Added" value={formatDate(baseDataset.added_date)} />
          </div>
        </div>
      )}
    </div>
  );
};

const DatasetMeta = ({ label, value, highlight }: { label: string, value: React.ReactNode, highlight?: boolean }) => (
  <div>
    <p className="text-slate-500 uppercase font-bold tracking-wider text-[9px]">{label}</p>
    <p className={cn("font-medium", highlight ? "text-cyan-400" : "text-slate-300")}>
      {value ?? 0}
    </p>
  </div>
);
