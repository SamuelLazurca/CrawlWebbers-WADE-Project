import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../../stores/filterStore';
import { StatCard } from '../cards/StatCard';
import { ChartCard } from '../cards/ChartCard';
import { ConceptCard } from '../cards/ConceptCard';
import {
  mockConcepts,
  mockChartData,
  mockTrendData,
} from '../../data/mockData';
import { Database, Files, Users, TrendingUp } from 'lucide-react';
import { CompareCard } from '../layout/CompareCard';
import { useSidebarContext } from '../../context/sidebarContext';
import type { TrendPoint } from '../../types';
import { getTrendData } from '../../lib/trends';

export const DashboardGrid: React.FC = () => {
  const { activeTab } = useFilterStore();
  const { baseDataset } = useSidebarContext();
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);


  useEffect(() => {
   const fetchTrendData = async (propertyUri: string, granularity: string = 'year') => {
      try {
        const response = await getTrendData(propertyUri, granularity);
        
        const data = response.data.map(point => ({
          label: point.label,
          count: point.count,
          //volume: point.value
        }));

        console.log("Fetched trend data:", data);
        
        setTrendData(data); 
      } catch (error) {
        console.error("Error fetching trends:", error);
      }
    };
    if (baseDataset) {
      fetchTrendData('http://schema.org/datePublished', 'year');
    }
  }, [baseDataset]);


  if (!baseDataset) {
    return (
      <div className='text-white text-center py-8'>
        Select a base dataset in the sidebar to view dashboard.
      </div>
    );
  }

  if (activeTab === 'analytics') {
    const formatSize = (b?: number) => {
      if (!b) return '—';
      if (b >= 1e9) return (b / 1e9).toFixed(2) + ' GB';
      if (b >= 1e6) return (b / 1e6).toFixed(2) + ' MB';
      if (b >= 1e3) return (b / 1e3).toFixed(2) + ' KB';
      return b + ' B';
    };
    return (
      <div className='space-y-6'>
        <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
          <StatCard
            title='Size'
            value={formatSize(baseDataset.size_in_bytes)}
            icon={<Database size={24} />}
            color='cyan'
          />
          <StatCard
            title='Number of Files'
            value={baseDataset.number_of_files?.toLocaleString() || '0'}
            color='emerald'
            icon={<Files size={24} />}
          />
          <StatCard
            title='Relationships'
            value='18.5K'
            trend='up'
            trendValue={8}
            icon={<Users size={24} />}
            color='amber'
          />
          <StatCard
            title='Growth Rate'
            value='48%'
            trend='up'
            trendValue={24}
            icon={<TrendingUp size={24} />}
            color='rose'
          />
        </div>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          <ChartCard
            title='Bar Chart'
            subtitle='Distribution over Years'
            type='bar'
            data={trendData.length > 0 ? trendData : []}
            dataKey='count'
            xKey='label'
          />
          <ChartCard
            title='Line Chart'
            subtitle='Growth over Years'
            type='line'
            data={trendData.length > 0 ? trendData : []}
            dataKey='count'
            xKey='label'
          />
        </div>
      </div>
    );
  }

  if (activeTab === 'graph') {
    return (
      <div className='space-y-6'>
        <div className='rounded-2xl p-8 bg-gradient-to-br from-slate-800/40 to-slate-900/20 border border-slate-700/50 backdrop-blur-sm h-96 flex items-center justify-center'>
          <div className='text-center'>
            <p className='text-slate-400 text-lg mb-2'>Graph Visualization</p>
            <p className='text-slate-500 text-sm'>
              Cytoscape.js ontology explorer will render here
            </p>
          </div>
        </div>

        <div>
          <h2 className='text-xl font-bold text-white mb-4'>
            Related Concepts
          </h2>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
            {mockConcepts.map((concept) => (
              <ConceptCard key={concept.uri} concept={concept} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === '3d') {
    return (
      <div className='rounded-2xl p-8 bg-gradient-to-br from-slate-800/40 to-slate-900/20 border border-slate-700/50 backdrop-blur-sm h-96 flex items-center justify-center'>
        <div className='text-center'>
          <p className='text-slate-400 text-lg mb-2'>3D Visualization</p>
          <p className='text-slate-500 text-sm'>
            React Three Fiber 3D ontology explorer will render here
          </p>
        </div>
      </div>
    );
  }

  if (activeTab === 'compare') {
    return <CompareCard />;
  }

  return null;
};
