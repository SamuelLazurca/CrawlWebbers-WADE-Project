import React, { useEffect, useState } from 'react';
import { ChevronDown, Database } from 'lucide-react';
import type { Dataset } from '../types/datasets';
import { getDatasets } from '../lib/datasets';
import clsx from 'clsx';
import { useSidebarContext } from '../context/sidebarContext';

export const DatasetSelector: React.FC = () => {
  const { baseDataset, setBaseDataset } = useSidebarContext();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    async function load() {
      const data = await getDatasets();
      setDatasets(data || []);
      if (!baseDataset && data && data.length > 0) {
        setBaseDataset(data[0]);
      }
    }
    load();
  }, []);

  if (!baseDataset && datasets.length === 0) {
    return (
      <div className="p-4 border-b border-slate-800">
        <div className="text-slate-400 text-sm">Loading datasets...</div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 border-b border-slate-800">
      <div className="relative">
        <button
          onClick={() => setOpen((s) => !s)}
          className="w-full flex items-center justify-between px-4 py-3 rounded-xl
            bg-slate-800/50 border border-slate-700 text-slate-200 hover:border-emerald-400 transition"
          aria-haspopup="listbox"
          aria-expanded={open}
        >
          <div className="flex items-center gap-2">
            <Database size={16} className="text-cyan-400" />
            <span className="font-medium line-clamp-1">
              {baseDataset?.name ?? 'Select a dataset'}
            </span>
          </div>
          <ChevronDown size={18} className={clsx('transition-transform', open && 'rotate-180')} />
        </button>

        {open && (
          <div className="absolute z-50 mt-2 w-full rounded-xl bg-slate-900 border border-slate-700 shadow-xl overflow-hidden">
            {datasets.map((ds) => (
              <button
                key={ds.id}
                onClick={() => {
                  setBaseDataset(ds);
                  setOpen(false);
                }}
                className={clsx(
                  'w-full text-left px-4 py-3 text-sm transition',
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
          <div>
            <p className="text-xs text-slate-400">Files</p>
            <p className="font-semibold text-cyan-400">{baseDataset.number_of_files ?? 0}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Downloads</p>
            <p className="font-semibold text-cyan-400">{baseDataset.number_of_downloads ?? 0}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Size</p>
            <p className="font-semibold text-slate-200">{formatSize(baseDataset.size_in_bytes)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Added</p>
            <p className="font-semibold text-slate-200">{formatDate(baseDataset.added_date)}</p>
          </div>
        </div>
      )}
    </div>
  );
};

const formatSize = (b?: number) => {
  if (!b) return '—';
  if (b >= 1e9) return (b / 1e9).toFixed(2) + ' GB';
  if (b >= 1e6) return (b / 1e6).toFixed(2) + ' MB';
  if (b >= 1e3) return (b / 1e3).toFixed(2) + ' KB';
  return b + ' B';
};

const formatDate = (s?: string) =>
  s ? new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(s)) : '—';
