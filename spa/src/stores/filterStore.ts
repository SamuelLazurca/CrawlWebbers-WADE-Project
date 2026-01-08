// src/stores/filterStore.ts
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

interface FilterState {
  selectedFilters: Map<string, Set<string>>;
  searchQuery: string;
  activeTab: 'analytics' | 'graph' | '3d' | 'compare';

  addFilter: (property: string, value: string) => void;
  removeFilter: (property: string, value: string) => void;
  clearFilters: () => void;
  setSearchQuery: (query: string) => void;
  setActiveTab: (tab: FilterState['activeTab']) => void;
  getFilterCount: () => number;
}

export const useFilterStore = create<FilterState>()(
  subscribeWithSelector((set, get) => ({
    selectedFilters: new Map(),
    searchQuery: '',
    activeTab: 'analytics',

    addFilter: (property, value) =>
      set((state) => {
        const updated = new Map(state.selectedFilters);
        const current = updated.get(property) || new Set();
        updated.set(property, new Set([...current, value]));
        return { selectedFilters: updated };
      }),

    removeFilter: (property, value) =>
      set((state) => {
        const updated = new Map(state.selectedFilters);
        const current = updated.get(property) || new Set();
        current.delete(value);
        if (current.size === 0) {
          updated.delete(property);
        } else {
          updated.set(property, current);
        }
        return { selectedFilters: updated };
      }),

    clearFilters: () => set({ selectedFilters: new Map() }),

    setSearchQuery: (query) => set({ searchQuery: query }),

    setActiveTab: (tab) => set({ activeTab: tab }),

    getFilterCount: () => {
      let count = 0;
      get().selectedFilters.forEach((set) => (count += set.size));
      return count;
    },
  }))
);
