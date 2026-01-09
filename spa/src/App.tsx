import { ModernSidebar } from './components/sidebar/ModernSidebar';
import { Header } from './components/layout/Header';
import { DashboardGrid } from './components/dashboard/DashboardGrid';
import { SidebarProvider } from './context/sidebarContext';

function App() {
  return (
    <div className='min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100'>
      <Header />
      <SidebarProvider>
        <ModernSidebar />

        <main className='fixed left-80 right-0 top-32 bottom-0 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent'>
          <div className='max-w-7xl mx-auto px-8 py-8'>
            <DashboardGrid />
          </div>
        </main>
      </SidebarProvider>
    </div>
  );
}

export default App;
