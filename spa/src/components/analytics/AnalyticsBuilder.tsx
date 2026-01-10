import React, { useState, useEffect } from 'react';
import { useSidebarContext } from '../../context/sidebarContext';
import { getCustomAnalytics } from '../../lib/analytics';
import { ChartCard } from '../cards/ChartCard';
import { Layout, Database, Calculator, Loader2 } from 'lucide-react';
import type { TrendPoint } from '../../types';

export const AnalyticsBuilder: React.FC = () => {
  const { baseDataset } = useSidebarContext();
  const [selectedDim, setSelectedDim] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('');
  const [agg, setAgg] = useState('COUNT');
  const [chartData, setChartData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedDim) {
      setChartData([]);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getCustomAnalytics(selectedDim, selectedMetric || null, agg, 20);
        console.log("Fetched analytics data:", data);
        setChartData(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Fetch error:", error);
        setChartData([]); 
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [selectedDim, selectedMetric, agg]);

  const selectStyles = "bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-3 py-2 outline-none focus:border-emerald-500 transition-colors text-sm w-full";

  return (
    <div className='space-y-6'>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6 p-6 bg-slate-900/50 rounded-2xl border border-slate-800 backdrop-blur-md'>
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
            <Layout size={14} /> Dimension (X-Axis)
          </label>
          <select
            value={selectedDim}
            onChange={(e) => setSelectedDim(e.target.value)}
            className={selectStyles}
          >
            <option value=''>Select Property...</option>
            {baseDataset?.dimensions.map((dim) => (
              <option key={dim.uri} value={dim.uri}>{dim.label}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
            <Database size={14} /> Metric (Y-Axis)
          </label>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className={selectStyles}
          >
            <option value=''>Frequency (Count)</option>
            {baseDataset?.metrics.map((met) => (
              <option key={met.uri} value={met.uri}>{met.label}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
            <Calculator size={14} /> Aggregation
          </label>
          <select 
            value={agg}
            onChange={(e) => setAgg(e.target.value)} 
            className={selectStyles}
            disabled={!selectedMetric}
          >
            <option value='COUNT'>Count</option>
            <option value='SUM'>Sum</option>
            <option value='AVG'>Average</option>
            <option value='MAX'>Maximum</option>
          </select>
        </div>
      </div>

      <div className="relative min-h-[400px]">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/40 backdrop-blur-sm z-10 rounded-2xl">
            <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
          </div>
        )}

        {selectedDim ? (
          <ChartCard
            title={`${agg} of ${selectedMetric ? 'Metric' : 'Records'}`}
            subtitle={`Grouped by ${selectedDim.split('#').pop()}`}
            data={chartData}
            type={agg === 'AVG' ? 'line' : 'bar'}
            dataKey='count'
            xKey='label'
            height={400}
          />
        ) : (
          <div className="h-[400px] border-2 border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-slate-500 bg-slate-900/20">
            <Layout size={48} className="mb-4 opacity-20" />
            <p>Select a dimension to start analysis</p>
          </div>
        )}
      </div>
    </div>
  );
};