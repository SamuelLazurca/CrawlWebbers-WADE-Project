import React, { useState, useEffect } from 'react';
import { useFilterStore } from '../../stores/filterStore';
import { useSidebarContext } from '../../context/sidebarContext';
import { PresetChart } from '../cards/PresetChart';
import { AnalyticsBuilder } from '../analytics/AnalyticsBuilder';
import CombinedGraphVis from '../visualizations/GraphVis';
import { CompareCard } from './CompareCard';
import { FilterPanel } from '../cards/FilterPanel';

export const DashboardGrid: React.FC = () => {
  const { activeTab } = useFilterStore();
  const { baseDataset } = useSidebarContext();

  const [slotConfigs, setSlotConfigs] = useState<Record<string, string>>({
    slot1: '',
    slot2: '',
    slot3: '',
    slot4: '',
  });

  const allOptions =
    baseDataset?.supported_visualizations.flatMap((m) => m.options) || [];

  useEffect(() => {
    if (allOptions.length > 0) {
      setSlotConfigs({
        slot1: allOptions[0]?.id || '',
        slot2: allOptions[1]?.id || '',
        slot3: allOptions[2]?.id || '',
        slot4: allOptions[3]?.id || '',
      });
    }
  }, [baseDataset]);

  const renderSlot = (slotId: string) => {
    const selectedOptionId = slotConfigs[slotId];
    const currentOption = allOptions.find((o) => o.id === selectedOptionId);

    return (
      <div className='relative group'>
        <div className='absolute top-6 right-6 z-30'>
          <select
            value={selectedOptionId}
            onChange={(e) =>
              setSlotConfigs((prev) => ({ ...prev, [slotId]: e.target.value }))
            }
            className='bg-slate-800 text-xs text-slate-300 border border-slate-700 rounded px-2 py-1 outline-none hover:border-emerald-500 transition-colors cursor-pointer truncate'
          >
            {allOptions.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {currentOption ? (
          <PresetChart option={currentOption} />
        ) : (
          <div className='h-[300px] border-2 border-dashed border-slate-800 rounded-2xl flex items-center justify-center text-slate-600'>
            Select a metric
          </div>
        )}
      </div>
    );
  };

  return (
    <div className='p-6 space-y-8'>
      {activeTab === 'presets' && (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          {renderSlot('slot1')}
          {renderSlot('slot2')}
          {renderSlot('slot3')}
          {renderSlot('slot4')}
        </div>
      )}

      {activeTab === 'builder' && <AnalyticsBuilder />}
      {activeTab === 'explorer' && <CombinedGraphVis />}
      {activeTab === 'compare' && <CompareCard />}
      {activeTab === 'filter' && (
        <FilterPanel datasetClass={'http://schema.org/Movie'} />
      )}
    </div>
  );
};
