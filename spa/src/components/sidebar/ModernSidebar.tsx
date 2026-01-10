import React from 'react';
import { ChevronDown, Filter } from 'lucide-react';
import { mockFilterFacets } from '../../data/mockData';
import clsx from 'clsx';
import { DatasetSelector } from '../DatasetsSelector';

export const ModernSidebar: React.FC = () => {
  return (
    <aside className='fixed left-0 top-0 h-screen w-80 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 border-r border-slate-800 flex flex-col shadow-2xl z-40'>
      <div className='p-6 bg-gradient-to-b from-slate-900/50 to-transparent backdrop-blur-sm'>
        <div className='flex items-center gap-3 mb-6'>
          <div className='w-10 h-10 bg-gradient-to-br from-cyan-400 to-emerald-400 rounded-xl flex items-center justify-center'>
            <Filter size={20} className='text-slate-950 font-bold' />
          </div>
          <div>
            <h2 className='font-bold text-white'>Filters</h2>
            <p className='text-xs text-slate-400'>Refine your search</p>
          </div>
        </div>

        <DatasetSelector />
      </div>
    </aside>
  );
};

interface FacetGroupProps {
  facet: typeof mockFilterFacets[0];
  isExpanded: boolean;
  onToggle: () => void;
  selectedValues: Set<string>;
  onSelect: (value: string) => void;
  onDeselect: (value: string) => void;
}

function FacetGroup({
  facet,
  isExpanded,
  onToggle,
  selectedValues,
  onSelect,
  onDeselect,
}: FacetGroupProps) {
  return (
    <div className='group'>
      <button
        onClick={onToggle}
        className='w-full flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-slate-800/30 to-transparent hover:from-slate-800/50 hover:to-slate-800/20 border border-slate-700/50 hover:border-slate-600 transition group'
      >
        <span className='font-semibold text-slate-200 group-hover:text-white transition'>
          {facet.property}
        </span>
        <div className='flex items-center gap-2'>
          <span className='text-xs px-2 py-1 rounded bg-slate-700/50 text-slate-400'>
            {facet.values.length}
          </span>
          <ChevronDown
            size={18}
            className={`text-slate-400 transition transform ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </div>
      </button>

      {isExpanded && (
        <div className='mt-2 ml-4 space-y-2 pl-4 border-l-2 border-gradient-to-b from-emerald-500/30 to-transparent'>
          {facet.values.map(({ label, count }) => {
            const isSelected = selectedValues.has(label);
            return (
              <label
                key={label}
                className={clsx(
                  'flex items-center gap-3 p-3 rounded-lg cursor-pointer transition',
                  'hover:bg-slate-800/40',
                  isSelected && 'bg-emerald-500/10 border border-emerald-500/30'
                )}
              >
                <input
                  type='checkbox'
                  checked={isSelected}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onSelect(label);
                    } else {
                      onDeselect(label);
                    }
                  }}
                  className='w-4 h-4 rounded accent-emerald-400 cursor-pointer'
                />
                <span
                  className={clsx(
                    'flex-1 text-sm transition',
                    isSelected
                      ? 'text-emerald-300 font-medium'
                      : 'text-slate-300'
                  )}
                >
                  {label}
                </span>
                <span
                  className={clsx(
                    'text-xs px-2 py-0.5 rounded-full',
                    isSelected
                      ? 'bg-emerald-500/30 text-emerald-300'
                      : 'bg-slate-700/40 text-slate-400'
                  )}
                >
                  {count}
                </span>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}
