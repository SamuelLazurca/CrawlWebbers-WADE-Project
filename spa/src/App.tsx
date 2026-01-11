import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DashboardGrid } from './components/layout/DashboardGrid';
import { SidebarProvider } from './context/sidebarContext';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = isSidebarOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [isSidebarOpen]);

  return (
    <div className='min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100'>
      <SidebarProvider>
        <Header onToggleSidebar={() => setIsSidebarOpen((v) => !v)} />

        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {isSidebarOpen && (
          <div
            className='fixed inset-0 bg-black/50 z-40 md:hidden'
            onClick={() => setIsSidebarOpen(false)}
            aria-hidden='true'
          />
        )}

        <main className='fixed left-0 md:left-80 right-0 top-32 bottom-0 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent'>
          <div className='max-w-7xl mx-auto px-8 py-8'>
            <DashboardGrid />
          </div>
        </main>
      </SidebarProvider>
    </div>
  );
}

export default App;
