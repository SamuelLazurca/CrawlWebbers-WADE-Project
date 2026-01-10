import React from 'react';
import { useFilterStore } from '../../stores/filterStore';
import { useSidebarContext } from '../../context/sidebarContext';
import { cn } from '../../lib/utils';
import { Wand2, Share2, Repeat, LayoutDashboard } from 'lucide-react';

// Actualizăm tab-urile pentru a corespunde cu logica modulară
const TABS = [
  { id: 'presets' as const, label: 'Presets', icon: LayoutDashboard },
  { id: 'builder' as const, label: 'Analytics Builder', icon: Wand2 },
  { id: 'explorer' as const, label: 'Graph Explorer', icon: Share2 },
  { id: 'compare' as const, label: 'Compare', icon: Repeat },
];

export const Header: React.FC = () => {
  const { activeTab, setActiveTab } = useFilterStore();
  const { baseDataset } = useSidebarContext();

  return (
    <header className='fixed top-0 left-80 right-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800'>
      {/* Top Row: Title & Active Dataset */}
      <div className='h-16 px-8 flex items-center justify-between'>
        <div className='flex items-center gap-4'>
          <div>
            <h1 className='text-xl font-bold text-white tracking-tight'>
              Semantic Data Explorer
            </h1>
            <p className='text-[10px] text-slate-500 uppercase tracking-widest font-bold'>
              Knowledge Graph Analysis
            </p>
          </div>

          {/* Indicator Dataset Activ */}
          {baseDataset && (
            <div className='flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full'>
              <div className='w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse' />
              <span className='text-xs font-medium text-emerald-400'>
                {baseDataset.name}
              </span>
            </div>
          )}
        </div>

        <div className='flex items-center gap-4'>
          {/* Aici poți adăuga un Search global sau User Profile */}
        </div>
      </div>

      {/* Bottom Row: Tab Navigation */}
      <div className='px-8 flex gap-1 bg-slate-900/40'>
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-6 py-3 font-medium text-sm transition-all relative',
                isActive
                  ? 'text-emerald-400'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              )}
            >
              <Icon size={16} />
              {tab.label}

              {/* Active Indicator Line */}
              {isActive && (
                <div className='absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 shadow-[0_-4px_12px_rgba(16,185,129,0.5)]' />
              )}
            </button>
          );
        })}
      </div>
    </header>
  );
};
