import React from 'react';
import { useFilterStore } from '../../stores/filterStore';
import { StatCard } from '../cards/StatCard';
import { ChartCard } from '../cards/ChartCard';
import { ConceptCard } from '../cards/ConceptCard';
import {
  mockConcepts,
  mockChartData,
  mockTrendData,
} from '../../data/mockData';
import { Database, Zap, Users, TrendingUp } from 'lucide-react';
import { CompareCard } from '../layout/CompareCard';

export const DashboardGrid: React.FC = () => {
  const { activeTab } = useFilterStore();

  if (activeTab === 'analytics') {
    return (
      <div className='space-y-6'>
        <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
          <StatCard
            title='Total Concepts'
            value='2,341'
            trend='up'
            trendValue={12}
            icon={<Database size={24} />}
            color='cyan'
          />
          <StatCard
            title='Active Datasets'
            value='12'
            description='2 processing'
            icon={<Zap size={24} />}
            color='emerald'
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
            title='Distribution by Category'
            subtitle='Top 5 categories'
            type='bar'
            data={mockChartData}
            dataKey='value'
            xKey='label'
          />
          <ChartCard
            title='Growth Trend'
            subtitle='Last 30 days'
            type='line'
            data={mockTrendData}
            dataKey='value'
            xKey='date'
          />
        </div>

        <ChartCard
          title='Composition Analysis'
          subtitle='Category breakdown'
          type='pie'
          data={mockChartData}
          dataKey='value'
          xKey='label'
          height={350}
        />
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
