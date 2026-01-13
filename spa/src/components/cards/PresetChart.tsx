import React, {useEffect, useState} from 'react';
import type {TrendPoint, VisualizationOption} from '../../types';
import {getTrendData} from '../../lib/trends';
import {ChartCard} from './ChartCard';
import {Loader2} from 'lucide-react';
import {useSidebarContext} from '../../context/sidebarContext';

interface PresetChartProps {
  option: VisualizationOption;
}

export const PresetChart: React.FC<PresetChartProps> = ({ option }) => {
  const { currentView } = useSidebarContext();
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  const isDateProperty =
    option.target_property.toLowerCase().includes('date') ||
    option.label.toLowerCase().includes('timeline');

  useEffect(() => {
    const loadData = async () => {
      if (!currentView) return;

      setLoading(true);
      try {
        const currentGran = isDateProperty ? 'year' : 'none';

        const result = await getTrendData(
          option.target_property,
          currentView.id,
          currentGran
        );

        setData(result.data);
      } catch (error) {
      } finally {
        setLoading(false);
      }
    };

    void loadData();
  }, [option.target_property, isDateProperty, currentView]);

  return (
    <div className='relative group'>
      {loading && (
        <div className='absolute inset-0 flex items-center justify-center bg-slate-900/20 backdrop-blur-[2px] z-20 rounded-2xl'>
          <Loader2 className='w-6 h-6 text-cyan-500 animate-spin' />
        </div>
      )}

      <ChartCard<TrendPoint>
        title={option.label}
        subtitle={currentView ? `${currentView.label} Analysis` : 'Loading...'}
        type={isDateProperty ? 'line' : 'bar'}
        data={data}
        dataKey='value'
        xKey='label'
        height={300}
      />
    </div>
  );
};
