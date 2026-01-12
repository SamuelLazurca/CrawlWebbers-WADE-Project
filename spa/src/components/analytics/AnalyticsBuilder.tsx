import React, {useEffect, useState} from 'react';
import {useSidebarContext} from '../../context/sidebarContext';
import {getCustomAnalytics} from '../../lib/analytics';
import {ChartCard} from '../cards/ChartCard';
import {Calculator, Database, Layout, Loader2} from 'lucide-react';
import type {TrendPoint} from '../../types';

export const AnalyticsBuilder: React.FC = () => {
  const { currentView } = useSidebarContext();
  const [selectedDim, setSelectedDim] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('');
  const [agg, setAgg] = useState('COUNT');
  const [chartData, setChartData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSelectedDim('');
    setSelectedMetric('');
    setAgg('COUNT');
    setChartData([]);
  }, [currentView]);

  useEffect(() => {
    if (!selectedDim || !currentView) {
      setChartData([]);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getCustomAnalytics(
          selectedDim,
          selectedMetric || null,
          currentView.id,
          agg,
          20
        );
        setChartData(Array.isArray(data) ? data : []);
      } catch (error) {
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [selectedDim, selectedMetric, agg, currentView]);

  const selectStyles = "bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-3 py-2 outline-none focus:border-emerald-500 transition-colors text-sm w-full";

  if (!currentView) {
    return (
      <div className="p-8 text-center text-slate-500 border-2 border-dashed border-slate-800 rounded-2xl">
        Please select a Data View from the sidebar to build analytics.
      </div>
    );
  }

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
            {currentView.dimensions.map((dim) => (
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
            {currentView.metrics.map((met) => (
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
            <option value='MIN'>Minimum</option>
          </select>
        </div>
      </div>

      <div className="relative min-h-100">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/40 backdrop-blur-sm z-10 rounded-2xl">
            <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
          </div>
        )}

        {selectedDim ? (
          <ChartCard
            title={`${agg} of ${selectedMetric ? (currentView.metrics.find(m => m.uri === selectedMetric)?.label || 'Metric') : 'Records'}`}
            subtitle={`Grouped by ${currentView.dimensions.find(d => d.uri === selectedDim)?.label || 'Dimension'}`}
            data={chartData}
            type={agg === 'AVG' ? 'line' : 'bar'}
            dataKey='value'
            xKey='label'
            height={400}
          />
        ) : (
          <div className="h-100 border-2 border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-slate-500 bg-slate-900/20">
            <Layout size={48} className="mb-4 opacity-20" />
            <p>Select a dimension above to start analysis</p>
          </div>
        )}
      </div>
    </div>
  );
};
