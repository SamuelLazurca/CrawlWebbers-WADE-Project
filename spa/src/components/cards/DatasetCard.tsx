import React from 'react';
import { Database } from 'lucide-react';
import type { Dataset } from '../../types/datasets';
import clsx from 'clsx';

interface DatasetCardProps {
  dataset: Dataset;
  onClick?: () => void;
}

export const DatasetCard: React.FC<DatasetCardProps> = ({ dataset, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={clsx(
        'relative overflow-hidden rounded-2xl p-6',
        'bg-gradient-to-br from-slate-800/40 to-slate-900/20',
        'border border-slate-700/50 backdrop-blur-sm',
        'hover:shadow-xl transition-all duration-300 group',
        onClick && 'cursor-pointer hover:scale-105 hover:-translate-y-1'
      )}
      aria-label={`Dataset ${dataset.name || 'Untitled'}`}
    >
      <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-cyan-500/5 to-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/10 group-hover:from-cyan-500/30 transition">
              <Database size={24} className="text-cyan-400" aria-hidden />
            </div>
            <h3 className="font-bold text-white group-hover:text-emerald-300 transition line-clamp-1">
              {dataset.url ? (
                <a
                  href={dataset.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline"
                >
                  {dataset.name || 'Untitled'}
                </a>
              ) : (
                dataset.name || 'Untitled'
              )}
            </h3>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 pt-4 border-t border-slate-700/50">
          <InfoItem label="Files" value={dataset.number_of_files || 0} highlight />
          <InfoItem label="Downloads" value={dataset.number_of_downloads || 0} highlight />
          <InfoItem label="Size" value={formatSize(dataset.size_in_bytes || 0)} highlight />
          <InfoItem label="Added" value={formatDate(dataset.added_date)} />
          <InfoItem
            label="Uploaded by"
            value={
              dataset.uploaded_by && dataset.uploaded_by_url ? (
                <a
                  href={dataset.uploaded_by_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline"
                >
                  {dataset.uploaded_by}
                </a>
              ) : (
                dataset.uploaded_by || 'N/A'
              )
            }
          />
        </div>
      </div>
    </div>
  );
};

interface InfoItemProps {
  label: string;
  value: React.ReactNode;
  highlight?: boolean;
}

const InfoItem: React.FC<InfoItemProps> = ({ label, value, highlight }) => (
  <div>
    <p className="text-xs text-slate-400 mb-1">{label}</p>
    <p className={clsx('font-semibold', highlight ? 'text-xl text-cyan-400' : 'text-sm text-slate-200')}>
      {value}
    </p>
  </div>
);

const formatSize = (sizeInBytes: number): string => {
  if (sizeInBytes >= 1_000_000_000) return (sizeInBytes / 1_000_000_000).toFixed(2) + ' GB';
  if (sizeInBytes >= 1_000_000) return (sizeInBytes / 1_000_000).toFixed(2) + ' MB';
  if (sizeInBytes >= 1_000) return (sizeInBytes / 1_000).toFixed(2) + ' KB';
  return sizeInBytes + ' B';
};

const formatDate = (dateStr?: string): string => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: 'short', day: 'numeric' }).format(date);
};
