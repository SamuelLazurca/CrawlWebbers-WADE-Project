import React, {createContext, useContext, useState} from 'react';
import type {Dataset, DataView} from '../types';

interface SidebarContextValue {
  baseDataset: Dataset | null;
  currentView: DataView | null;
  setBaseDataset: (d: Dataset | null) => void;
  setCurrentView: (v: DataView | null) => void;
}

const SidebarContext = createContext<SidebarContextValue | undefined>(undefined);

export const SidebarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [baseDataset, setBaseDataset] = useState<Dataset | null>(null);
  const [currentView, setCurrentView] = useState<DataView | null>(null);

  const handleSetDataset = (d: Dataset | null) => {
    setBaseDataset(d);

    if (d && d.views.length > 0) {
      setCurrentView(d.views[0]);
    } else {
      setCurrentView(null);
    }
  };

  return (
    <SidebarContext.Provider
      value={{
        baseDataset,
        currentView,
        setBaseDataset: handleSetDataset,
        setCurrentView
      }}
    >
      {children}
    </SidebarContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useSidebarContext = (): SidebarContextValue => {
  const ctx = useContext(SidebarContext);
  if (!ctx) {
    throw new Error('useSidebarContext must be used within SidebarProvider');
  }
  return ctx;
};
