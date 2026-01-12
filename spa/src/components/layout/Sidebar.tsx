import React from 'react';
import { X } from 'lucide-react';
import { DatasetSelector } from '../DatasetSelector.tsx';
import { cn } from '../../lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <aside
      className={cn(
        'fixed top-0 left-0 h-screen w-80 bg-linear-to-b from-slate-950 via-slate-900 to-slate-950 border-r border-slate-800 flex flex-col shadow-2xl z-50 transform transition-transform duration-300 ease-in-out',
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      )}
      aria-hidden={!isOpen && true}
    >
      <div className='p-4 md:hidden flex justify-end'>
        <button
          onClick={onClose}
          className='p-2 rounded-md bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700 text-slate-100'
          aria-label='Close sidebar'
        >
          <X size={18} />
        </button>
      </div>

      <div className='p-6 bg-linear-to-b from-slate-900/50 to-transparent backdrop-blur-sm'>
        <div className='flex items-center gap-3 mb-6'>
          <div>
            <h2 className='font-bold text-white text-4xl tracking-tight'>
              DaVi
            </h2>
            <p className='text-xs text-slate-400 font-medium line-clamp-2'>
              View and Explore Data from{' '}
              <a
                href='https://academictorrents.com'
                target='_blank'
                rel='noopener noreferrer'
                className='text-emerald-400 hover:underline'
              >
                Academic Torrents
              </a>
            </p>
          </div>
        </div>

        <DatasetSelector />
      </div>
    </aside>
  );
};
