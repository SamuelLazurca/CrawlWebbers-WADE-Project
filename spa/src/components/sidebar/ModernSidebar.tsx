import React, { useState } from 'react';
import { ChevronDown, Search, Filter, TrendingUp } from 'lucide-react';
import { useFilterStore } from '../../stores/filterStore';
import { mockFilterFacets } from '../../data/mockData';
import clsx from 'clsx';

export const ModernSidebar: React.FC = () => {
  const [expandedFacets, setExpandedFacets] = useState<Set<string>>(
    new Set(['Category', 'Status'])
  );
  const [search, setSearch] = useState('');
  const {
    selectedFilters,
    addFilter,
    removeFilter,
    clearFilters,
    getFilterCount,
  } = useFilterStore();

  const toggleFacet = (property: string) => {
    const updated = new Set(expandedFacets);
    if (updated.has(property)) {
      updated.delete(property);
    } else {
      updated.add(property);
    }
    setExpandedFacets(updated);
  };

  const filterCount = getFilterCount();

  const filteredFacets = mockFilterFacets
    .map((facet) => ({
      ...facet,
      values: facet.values.filter((v) =>
        v.label.toLowerCase().includes(search.toLowerCase())
      ),
    }))
    .filter((facet) => facet.values.length > 0);

  return (
    <aside className='fixed left-0 top-0 h-screen w-80 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 border-r border-slate-800 flex flex-col shadow-2xl z-40'>
      <div className='p-6 border-b border-slate-800 bg-gradient-to-b from-slate-900/50 to-transparent backdrop-blur-sm'>
        <div className='flex items-center gap-3 mb-6'>
          <div className='w-10 h-10 bg-gradient-to-br from-cyan-400 to-emerald-400 rounded-xl flex items-center justify-center'>
            <Filter size={20} className='text-slate-950 font-bold' />
          </div>
          <div>
            <h2 className='font-bold text-white'>Filters</h2>
            <p className='text-xs text-slate-400'>Refine your search</p>
          </div>
        </div>

        <div className='relative group'>
          <Search className='absolute left-3 top-3 text-slate-500 group-focus-within:text-emerald-400 transition size-4' />
          <input
            type='text'
            placeholder='Search filters...'
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className='w-full pl-10 pr-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-400/50 focus:border-emerald-400 transition'
          />
        </div>

        {filterCount > 0 && (
          <div className='mt-3 flex items-center justify-between p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg'>
            <span className='text-sm text-emerald-300 font-medium flex items-center gap-2'>
              <TrendingUp size={16} />
              {filterCount} active filter{filterCount !== 1 ? 's' : ''}
            </span>
            <button
              onClick={() => clearFilters()}
              className='text-xs text-emerald-400 hover:text-emerald-300 font-medium transition'
            >
              Clear
            </button>
          </div>
        )}
      </div>

      <div className='flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent'>
        <div className='p-4 space-y-3'>
          {filteredFacets.length === 0 ? (
            <div className='text-center py-8'>
              <p className='text-slate-400 text-sm'>
                No filters match your search
              </p>
            </div>
          ) : (
            filteredFacets.map((facet) => (
              <FacetGroup
                key={facet.property}
                facet={facet}
                isExpanded={expandedFacets.has(facet.property)}
                onToggle={() => toggleFacet(facet.property)}
                selectedValues={
                  selectedFilters.get(facet.property) || new Set()
                }
                onSelect={(value) => addFilter(facet.property, value)}
                onDeselect={(value) => removeFilter(facet.property, value)}
              />
            ))
          )}
        </div>
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
