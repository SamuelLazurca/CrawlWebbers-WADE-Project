import React from 'react';
import {useFilterStore} from '../../stores/filterStore';
import {useSidebarContext} from '../../context/sidebarContext';
import {cn} from '../../lib/utils';
import {LayoutDashboard, Menu, Repeat, Share2, Wand2} from 'lucide-react';

const TABS = [
  { id: 'presets' as const, label: 'Presets', icon: LayoutDashboard },
  { id: 'builder' as const, label: 'Analytics Builder', icon: Wand2 },
  { id: 'explorer' as const, label: 'Graph Explorer', icon: Share2 },
  { id: 'compare' as const, label: 'Compare', icon: Repeat },
  { id: 'filter' as const, label: 'Filter Data', icon: Repeat },
];

interface HeaderProps {
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const { activeTab, setActiveTab } = useFilterStore();
  const { baseDataset } = useSidebarContext();

  return (
    <header
      className={cn(
        'fixed top-0 right-0 z-40',
        'left-0 md:left-80',
        'bg-slate-950/80 backdrop-blur-xl border-b border-slate-800'
      )}
    >
      <div className='h-16 px-4 md:px-8 flex items-center justify-between gap-4'>
        <div className='flex items-center gap-3 min-w-0'>
          {/* Hamburger – mobile only */}
          <button
            onClick={onToggleSidebar}
            className='md:hidden p-2 rounded-md bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700 text-slate-100'
            aria-label='Toggle sidebar'
          >
            <Menu size={20} />
          </button>

          <div className='min-w-0'>
            <h1 className='text-base md:text-xl font-bold text-white tracking-tight truncate'>
              Semantic Data Explorer
            </h1>
            <p className='hidden sm:block text-[10px] text-slate-500 uppercase tracking-widest font-bold'>
              Knowledge Graph Analysis
            </p>
          </div>

          {baseDataset && (
            <div className='hidden md:flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full'>
              <span className='relative flex h-2 w-2'>
                <span className='animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75' />
                <span className='relative inline-flex rounded-full h-2 w-2 bg-emerald-500' />
              </span>
              <span className='text-xs font-medium text-emerald-400 truncate max-w-40'>
                {baseDataset.name}
              </span>
            </div>
          )}
        </div>

        <div className='flex items-center gap-3'></div>
      </div>

      <div className='px-2 md:px-8 bg-slate-900/40 border-t border-slate-800'>
        <div className='flex gap-1 overflow-x-auto scrollbar-thin scrollbar-thumb-slate-700'>
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'relative flex items-center gap-2 px-4 md:px-6 py-3 text-sm font-medium whitespace-nowrap transition-colors',
                  isActive
                    ? 'text-emerald-400'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                )}
              >
                <Icon size={16} />
                {tab.label}

                {isActive && (
                  <span className='absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 shadow-[0_-4px_12px_rgba(16,185,129,0.5)]' />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
