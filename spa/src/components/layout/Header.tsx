import React from 'react';
import {useFilterStore} from '../../stores/filterStore';
import {cn} from '../../lib/utils';

const TABS = [
  { id: 'analytics' as const, label: 'Analytics' },
  { id: 'graph' as const, label: 'Graph' },
  { id: '3d' as const, label: '3D' },
  { id: 'compare' as const, label: 'Compare' },
];

export const Header: React.FC = () => {
  const { activeTab, setActiveTab } = useFilterStore();

  return (
    <header className="fixed top-0 left-80 right-0 h-20 bg-linear-to-b from-slate-950/80 to-slate-900/50 backdrop-blur-xl border-b border-slate-800 z-40">
      <div className="h-full px-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Semantic Data Explorer
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-medium">
            Knowledge graph visualization & analysis
          </p>
        </div>
      </div>

      <div className="absolute bottom-0 left-80 right-0 px-8 flex gap-2 border-t border-slate-800 bg-slate-900/30">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "px-4 py-3 font-medium text-sm transition-all border-b-2",
              activeTab === tab.id
                ? "text-emerald-400 border-emerald-400 bg-emerald-500/5"
                : "text-slate-400 border-transparent hover:text-slate-200 hover:bg-slate-800/50"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </header>
  );
};
