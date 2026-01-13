import React, {useEffect, useMemo, useState} from 'react';
import {X} from 'lucide-react';
import {getDatasets} from '../../lib/datasets';
import {useSidebarContext} from '../../context/sidebarContext';
import {cn, formatDate, formatSize} from '../../lib/utils';
import type {Dataset} from '../../types';

export const CompareCard: React.FC = () => {
  const { baseDataset } = useSidebarContext();
  const [all, setAll] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    async function load() {
      const data = await getDatasets();
      setAll(data || []);
      setLoading(false);
    }
    void load();
  }, []);

  const options = useMemo(() => {
    if (!baseDataset) return all;
    return all.filter((d) => d.id !== baseDataset.id);
  }, [all, baseDataset]);

  const selectedDatasets = useMemo(
    () => selectedIds.map((id) => all.find((d) => d.id === id)).filter(Boolean) as Dataset[],
    [selectedIds, all]
  );

  if (loading) return <div className="text-white text-center py-8">Loading datasets...</div>;
  if (!baseDataset) return <div className="text-white text-center py-8">Select a base dataset to compare.</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-white">Compare Datasets</h2>

      <div className="flex items-center gap-3">
        <label className="text-sm text-slate-300">Compare with:</label>
        <div className="relative">
          <select
            value=""
            onChange={(e) => {
              const id = e.target.value;
              if (id) setSelectedIds((prev) => (prev.includes(id) ? prev : [...prev, id]));
            }}
            className="bg-slate-800/50 border text-xs border-slate-700 text-slate-200 px-4 py-2 rounded-lg cursor-pointer hover:border-slate-600 focus:outline-none focus:border-cyan-400 w-50 truncate"
          >
            <option value="">Select dataset...</option>
            {options.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name || 'Untitled'}
              </option>
            ))}
          </select>
        </div>

        <div className="flex gap-2 flex-wrap">
          {selectedDatasets.map((d) => (
            <div
              key={d.id}
              className="px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700 text-sm flex items-center gap-2 animate-in fade-in zoom-in-95"
            >
              <span className='line-clamp-1 max-w-37.5'>{d.name}</span>
              <button
                onClick={() => setSelectedIds((prev) => prev.filter((id) => id !== d.id))}
                className="text-xs text-slate-400 hover:text-rose-400 ml-2"
                aria-label={`Remove ${d.name}`}
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto pb-4">
        <div className="min-w-full grid grid-cols-1 md:grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-4">
          <ComparisonColumn title="Base" dataset={baseDataset} highlightDifferencesWith={selectedDatasets} />
          {selectedDatasets.map((d) => (
            <ComparisonColumn key={d.id} title={d.name || 'Dataset'} dataset={d} highlightDifferencesWith={[baseDataset]} />
          ))}
        </div>
      </div>
    </div>
  );
};

const ComparisonColumn: React.FC<{
  title?: string;
  dataset: Dataset;
  highlightDifferencesWith?: Dataset[];
}> = ({ title, dataset, highlightDifferencesWith = [] }) => {

  const isDifferent = (key: keyof Dataset) => {
    return highlightDifferencesWith.some((other) => {
      const valA = dataset[key];
      const valB = other[key];
      if (typeof valA === 'object' || typeof valB === 'object') return false;
      return valA !== valB;
    });
  };

  return (
    <div className="rounded-2xl p-4 bg-linear-to-br from-slate-800/40 to-slate-900/20 border border-slate-700/50 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-white truncate max-w-50">{title}</h3>
        {dataset.url && (
          <a href={dataset.url} target="_blank" rel="noopener noreferrer" className="text-xs text-emerald-400 hover:underline">
            Source
          </a>
        )}
      </div>

      <div className="space-y-3">
        <MetaRow label="Files" value={dataset.number_of_files ?? 0} highlight={isDifferent('number_of_files')} />
        <MetaRow label="Downloads" value={dataset.number_of_downloads ?? 0} highlight={isDifferent('number_of_downloads')} />
        <MetaRow label="Size" value={formatSize(dataset.size_in_bytes)} highlight={isDifferent('size_in_bytes')} />
        <MetaRow label="Added" value={formatDate(dataset.added_date)} highlight={isDifferent('added_date')} />
        <MetaRow label="Views" value={dataset.views.length} highlight={false} />

        <MetaRow
          label="Uploaded by"
          value={
            dataset.uploaded_by_url ? (
              <a href={dataset.uploaded_by_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                {dataset.uploaded_by || '—'}
              </a>
            ) : (dataset.uploaded_by || '—')
          }
          highlight={isDifferent('uploaded_by')}
        />
      </div>
    </div>
  );
};

const MetaRow: React.FC<{ label: string; value: React.ReactNode; highlight?: boolean }> = ({ label, value, highlight }) => (
  <div className="flex items-center justify-between border-b border-slate-800/50 pb-2 last:border-0 last:pb-0">
    <div className="text-xs text-slate-400">{label}</div>
    <div className={cn('font-semibold truncate max-w-37.5 text-sm', highlight ? 'text-rose-300' : 'text-slate-200')}>
      {value}
    </div>
  </div>
);
