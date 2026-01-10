import React from 'react';
import {ChevronDown, Filter} from 'lucide-react';
import {DatasetSelector} from '../DatasetsSelector';
import {cn} from '../../lib/utils';
import type {FilterFacet} from '../../types';

// Temporary local data until FilterService is fully connected to the Store
const DEMO_FACETS: FilterFacet[] = [
  {
    property: 'Category',
    values: [
      { label: 'Technology', count: 2341 },
      { label: 'Semantic Web', count: 1824 },
      { label: 'Data Science', count: 1456 },
    ],
    isExpanded: true,
  },
  {
    property: 'Status',
    values: [
      { label: 'Active', count: 4200 },
      { label: 'Deprecated', count: 342 },
    ],
    isExpanded: true,
  },
];

export const ModernSidebar: React.FC = () => {
  const handleSelect = (val: string) => console.log('Select', val);
  const handleDeselect = (val: string) => console.log('Deselect', val);

  return (
    <aside className="fixed left-0 top-0 h-screen w-80 bg-linear-to-b from-slate-950 via-slate-900 to-slate-950 border-r border-slate-800 flex flex-col shadow-2xl z-40">
      <div className="p-6 bg-linear-to-b from-slate-900/50 to-transparent backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-linear-to-br from-cyan-400 to-emerald-400 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-900/20">
            <Filter size={20} className="text-slate-950 font-bold" />
          </div>
          <div>
            <h2 className="font-bold text-white text-lg tracking-tight">Filters</h2>
            <p className="text-xs text-slate-400 font-medium">Refine your search</p>
          </div>
        </div>

        <DatasetSelector />
      </div>

      <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-4 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        {DEMO_FACETS.map((facet, idx) => (
          <FacetGroup
            key={facet.property + idx}
            facet={facet}
            isExpanded={true}
            onToggle={() => {}}
            selectedValues={new Set()}
            onSelect={handleSelect}
            onDeselect={handleDeselect}
          />
        ))}
      </div>
    </aside>
  );
};

interface FacetGroupProps {
  facet: FilterFacet;
  isExpanded: boolean;
  onToggle: () => void;
  selectedValues: Set<string>;
  onSelect: (value: string) => void;
  onDeselect: (value: string) => void;
}

const FacetGroup: React.FC<FacetGroupProps> = ({
                                                 facet,
                                                 isExpanded,
                                                 onToggle,
                                                 selectedValues,
                                                 onSelect,
                                                 onDeselect,
                                               }) => {
  return (
    <div className="group">
      <button
        onClick={onToggle}
        className={cn(
          "w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200",
          "bg-slate-800/30 border border-slate-700/30",
          "hover:bg-slate-800/60 hover:border-slate-600"
        )}
      >
        <span className="font-semibold text-slate-200 text-sm group-hover:text-white transition">
          {facet.property}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-700/50 text-slate-400">
            {facet.values.length}
          </span>
          <ChevronDown
            size={16}
            className={cn("text-slate-400 transition-transform duration-200", isExpanded && "rotate-180")}
          />
        </div>
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-1 ml-1 pl-3 border-l-2 border-slate-800">
          {facet.values.map(({ label, count }) => {
            const isSelected = selectedValues.has(label);
            return (
              <label
                key={label}
                className={cn(
                  'flex items-center gap-3 p-2 rounded-md cursor-pointer transition-all duration-200 group/item',
                  'hover:bg-slate-800/40',
                  isSelected && 'bg-emerald-500/10'
                )}
              >
                <div className="relative flex items-center">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={(e) => (e.target.checked ? onSelect(label) : onDeselect(label))}
                    className="peer appearance-none w-4 h-4 rounded border border-slate-600 bg-slate-800 checked:bg-emerald-500 checked:border-emerald-500 transition-colors cursor-pointer"
                  />
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 peer-checked:opacity-100 text-slate-950">
                    <svg width="10" height="8" viewBox="0 0 10 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 4L3.5 6.5L9 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                </div>

                <span className={cn('flex-1 text-sm transition', isSelected ? 'text-emerald-300 font-medium' : 'text-slate-400 group-hover/item:text-slate-300')}>
                  {label}
                </span>

                <span className={cn('text-[10px] px-1.5 rounded-full', isSelected ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-500')}>
                  {count}
                </span>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
};
