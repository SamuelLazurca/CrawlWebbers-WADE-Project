import React, { useMemo, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore';
import { useSidebarContext } from '../../context/sidebarContext';
import { PresetChart } from '../cards/PresetChart';
import { AnalyticsBuilder } from '../analytics/AnalyticsBuilder';
import CombinedGraphVis from '../visualizations/GraphVis';
import { CompareCard } from '../cards/CompareCard';
import { FilterPanel } from '../cards/FilterPanel';

export const DashboardGrid: React.FC = () => {
  const { activeTab } = useFilterStore();
  const { baseDataset, currentView } = useSidebarContext();

  const allOptions = useMemo(() => {
    return (
      currentView?.supported_visualizations.flatMap((m) => m.options) || []
    );
  }, [currentView]);

  const [prevViewId, setPrevViewId] = useState<string | undefined>(
    currentView?.id
  );

  const [slotConfigs, setSlotConfigs] = useState<Record<string, string>>(() => {
    if (allOptions.length > 0) {
      return {
        slot1: allOptions[0]?.id || '',
        slot2: allOptions[1]?.id || '',
        slot3: allOptions[2]?.id || '',
        slot4: allOptions[3]?.id || '',
      };
    }
    return { slot1: '', slot2: '', slot3: '', slot4: '' };
  });

  if (currentView?.id !== prevViewId) {
    setPrevViewId(currentView?.id);

    const newDefaults =
      allOptions.length > 0
        ? {
            slot1: allOptions[0]?.id || '',
            slot2: allOptions[1]?.id || '',
            slot3: allOptions[2]?.id || '',
            slot4: allOptions[3]?.id || '',
          }
        : { slot1: '', slot2: '', slot3: '', slot4: '' };

    setSlotConfigs(newDefaults);
  }

  const renderSlot = (slotId: string) => {
    const selectedOptionId = slotConfigs[slotId];
    const currentOption = allOptions.find((o) => o.id === selectedOptionId);

    return (
      <div className='relative group'>
        {allOptions.length > 0 && (
          <div className='absolute top-6 right-6 z-30 opacity-0 group-hover:opacity-100 transition-opacity'>
            <select
              value={selectedOptionId}
              onChange={(e) =>
                setSlotConfigs((prev) => ({
                  ...prev,
                  [slotId]: e.target.value,
                }))
              }
              className='bg-slate-800 text-xs text-slate-300 border border-slate-700 rounded px-2 py-1 outline-none hover:border-emerald-500 transition-colors cursor-pointer truncate max-w-37.5'
            >
              {allOptions.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {currentOption ? <PresetChart option={currentOption} /> : null}
      </div>
    );
  };

  if (!baseDataset) {
    return (
      <div className='p-10 text-center text-slate-500'>
        Please select a dataset to begin.
      </div>
    );
  }

  return (
    <div className='p-6 space-y-8'>
      {activeTab === 'presets' && (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          {allOptions.length > 0 ? (
            allOptions.map((_, index) => renderSlot(`slot${index + 1}`))
          ) : (
            <div className='text-center text-slate-500 col-span-2'>
              No preset visualizations available for this view.
            </div>
          )}
        </div>
      )}

      {activeTab === 'builder' && <AnalyticsBuilder />}
      {activeTab === 'explorer' && <CombinedGraphVis />}
      {activeTab === 'compare' && <CompareCard />}

      {activeTab === 'filter' && currentView?.target_class && (
        <FilterPanel datasetClass={currentView.target_class} />
      )}
      {activeTab === 'filter' && !currentView?.target_class && (
        <div className='text-center text-slate-500 py-10'>
          This view does not support filtering configuration.
        </div>
      )}
    </div>
  );
};
