import React, { createContext, useContext, useState } from 'react';
import type { Dataset } from '../types';

interface SidebarContextValue {
  baseDataset: Dataset | null;
  setBaseDataset: (d: Dataset | null) => void;
}

const SidebarContext = createContext<SidebarContextValue | undefined>(undefined);

export const SidebarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [baseDataset, setBaseDataset] = useState<Dataset | null>(null);

  return (
    <SidebarContext.Provider value={{ baseDataset, setBaseDataset }}>
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
