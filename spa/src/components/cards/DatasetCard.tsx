import React from 'react';
import { Database, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import type { Dataset } from '../../types';
import clsx from 'clsx';

interface DatasetCardProps {
  dataset: Dataset;
  onClick?: () => void;
}

export const DatasetCard: React.FC<DatasetCardProps> = ({
  dataset,
  onClick,
}) => {
  const statusConfig = {
    active: {
      icon: CheckCircle,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      label: 'Active',
    },
    processing: {
      icon: Clock,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      label: 'Processing',
    },
    inactive: {
      icon: AlertCircle,
      color: 'text-slate-400',
      bg: 'bg-slate-500/10',
      label: 'Inactive',
    },
  };

  const status = statusConfig[dataset.status];
  const StatusIcon = status.icon;

  const formatNumber = (num: number) => {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div
      onClick={onClick}
      className={clsx(
        'relative overflow-hidden rounded-2xl p-6',
        'bg-gradient-to-br from-slate-800/40 to-slate-900/20',
        'border border-slate-700/50',
        'backdrop-blur-sm',
        'hover:shadow-xl transition-all duration-300 group',
        onClick && 'cursor-pointer hover:scale-105 hover:-translate-y-1'
      )}
    >
      <div className='absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-cyan-500/5 to-emerald-500/5 rounded-full blur-3xl pointer-events-none' />

      <div className='relative z-10'>
        <div className='flex items-start justify-between mb-4'>
          <div className='flex items-center gap-3'>
            <div className='p-3 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/10 group-hover:from-cyan-500/30 transition'>
              <Database size={24} className='text-cyan-400' />
            </div>
            <div>
              <h3 className='font-bold text-white group-hover:text-emerald-300 transition'>
                {dataset.name}
              </h3>
              <p className='text-xs text-slate-400 mt-0.5'>{dataset.id}</p>
            </div>
          </div>
          <div className={clsx('p-2 rounded-lg', status.bg)}>
            <StatusIcon size={18} className={status.color} />
          </div>
        </div>

        <p className='text-sm text-slate-300 mb-4 line-clamp-2'>
          {dataset.description}
        </p>

        <div className='grid grid-cols-2 gap-3 mb-4 pt-4 border-t border-slate-700/50'>
          <div>
            <p className='text-xs text-slate-400 mb-1'>Concepts</p>
            <p className='text-xl font-bold text-cyan-400'>
              {formatNumber(dataset.conceptCount)}
            </p>
          </div>
          <div>
            <p className='text-xs text-slate-400 mb-1'>Updated</p>
            <p className='text-sm font-semibold text-slate-200'>
              {dataset.lastUpdated}
            </p>
          </div>
        </div>

        <div
          className={clsx(
            'inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium',
            status.bg,
            status.color
          )}
        >
          <div className='w-1.5 h-1.5 rounded-full bg-current opacity-60 animate-pulse' />
          {status.label}
        </div>
      </div>
    </div>
  );
};
