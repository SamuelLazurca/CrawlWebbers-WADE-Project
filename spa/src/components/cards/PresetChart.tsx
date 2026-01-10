import React, { useEffect, useState } from 'react';
import type { VisualizationOption, TrendPoint } from '../../types/index';
import { getTrendData } from '../../lib/trends';
import { ChartCard } from '../cards/ChartCard';
import { Loader2, Calendar } from 'lucide-react';

interface PresetChartProps {
  option: VisualizationOption;
}

export const PresetChart: React.FC<PresetChartProps> = ({ option }) => {
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [granularity, setGranularity] = useState<'year' | 'none'>('none');

  const isDateProperty =
    option.target_property.toLowerCase().includes('date') ||
    option.label.toLowerCase().includes('timeline');

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const currentGran = isDateProperty ? 'year' : 'none';
        const result = await getTrendData(option.target_property, currentGran);
        setData(result.data);
      } catch (error) {
        console.error('Failed to load preset data:', error);
      } finally {
        setLoading(false);
      }
    };

    void loadData();
  }, [option.target_property, isDateProperty]);

  return (
    <div className='relative group'>
      {isDateProperty && (
        <div className='absolute top-4 right-12 z-10 flex items-center gap-1 text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded border border-slate-700'>
          <Calendar size={12} />
          <span>Grouped by Year</span>
        </div>
      )}

      {loading && (
        <div className='absolute inset-0 flex items-center justify-center bg-slate-900/20 backdrop-blur-[2px] z-20 rounded-2xl'>
          <Loader2 className='w-6 h-6 text-cyan-500 animate-spin' />
        </div>
      )}

      <ChartCard
        title={option.label}
        subtitle={`Source: ${option.target_property}`}
        type={isDateProperty ? 'line' : 'bar'}
        data={data}
        dataKey='count'
        xKey='label'
        height={300}
      />
    </div>
  );
};
