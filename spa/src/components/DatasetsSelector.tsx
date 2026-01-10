import React, {useEffect, useState} from 'react';
import {ChevronDown, Database} from 'lucide-react';
import {getDatasets} from '../lib/datasets';
import {useSidebarContext} from '../context/sidebarContext';
import {cn, formatDate, formatSize} from '../lib/utils';
import type {Dataset} from '../types';

export const DatasetSelector: React.FC = () => {
  const { baseDataset, setBaseDataset } = useSidebarContext();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isOpen, setIsOpen] = useState(false);

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
  });

  if (!baseDataset && datasets.length === 0) {
    return (
      <div className="p-4 border-b border-slate-800">
        <div className="text-slate-400 text-sm animate-pulse">Loading datasets...</div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 border-b border-slate-800">
      <div className="relative">
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          className={cn(
            "w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all",
            "bg-slate-800/50 border border-slate-700 text-slate-200",
            "hover:border-emerald-400 hover:shadow-lg hover:shadow-emerald-900/10",
            isOpen && "border-emerald-400 ring-1 ring-emerald-400/20"
          )}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
        >
          <div className="flex items-center gap-2">
            <Database size={16} className="text-cyan-400 shrink-0" />
            <span className="font-medium text-sm line-clamp-1">
              {baseDataset?.name ?? 'Select a dataset'}
            </span>
          </div>
          <ChevronDown
            size={18}
            className={cn('transition-transform duration-200', isOpen && 'rotate-180')}
          />
        </button>

        {isOpen && (
          <div className="absolute z-50 mt-2 w-full rounded-xl bg-slate-900 border border-slate-700 shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
            {datasets.map((ds) => (
              <button
                key={ds.id}
                onClick={() => {
                  setBaseDataset(ds);
                  setIsOpen(false);
                }}
                className={cn(
                  'w-full text-left px-4 py-3 text-xs line-clamp-1 transition',
                  'hover:bg-slate-800/60',
                  ds.id === baseDataset?.id ? 'bg-emerald-500/10 text-emerald-300' : 'text-slate-300'
                )}
              >
                {ds.name || 'Untitled'}
              </button>
            ))}
          </div>
        )}
      </div>

      {baseDataset && (
        <div className="grid grid-cols-2 gap-2 text-sm">
          <DatasetMeta label="Files" value={baseDataset.number_of_files} highlight />
          <DatasetMeta label="Downloads" value={baseDataset.number_of_downloads} highlight />
          <DatasetMeta label="Size" value={formatSize(baseDataset.size_in_bytes)} />
          <DatasetMeta label="Added" value={formatDate(baseDataset.added_date)} />
        </div>
      )}
    </div>
  );
};

const DatasetMeta = ({ label, value, highlight }: { label: string, value: React.ReactNode, highlight?: boolean }) => (
  <div>
    <p className="text-xs text-slate-400">{label}</p>
    <p className={cn("font-semibold", highlight ? "text-cyan-400" : "text-slate-200")}>
      {value ?? 0}
    </p>
  </div>
);
