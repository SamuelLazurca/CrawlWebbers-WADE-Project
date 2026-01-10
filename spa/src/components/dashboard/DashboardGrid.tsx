import React, {useEffect, useState} from 'react';
import {Database, Files, TrendingUp, Users} from 'lucide-react';

import {useFilterStore} from '../../stores/filterStore';
import {useSidebarContext} from '../../context/sidebarContext';
import {getTrendData} from '../../lib/trends';
import {formatSize} from '../../lib/utils';
import type {TrendPoint} from '../../types';

import {StatCard} from '../cards/StatCard';
import {ChartCard} from '../cards/ChartCard';
import {CompareCard} from '../layout/CompareCard';
import {GraphVis} from '../visualizations/GraphVis';
import {ThreeDGraphVis} from '../visualizations/ThreeDGraphVis';

export const DashboardGrid: React.FC = () => {
  const { activeTab } = useFilterStore();
  const { baseDataset } = useSidebarContext();
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);

  useEffect(() => {
    if (!baseDataset?.supported_visualizations) return;

    const fetchTrends = async (propertyUri: string, granularity: string = 'year') => {
      try {
        const response = await getTrendData(propertyUri, granularity);
        const data = response.data.map((point) => ({
          label: point.label,
          count: point.count,
        }));
        setTrendData(data);
      } catch (error) {
        console.error('Error fetching trends:', error);
      }
    };

    // 1. Find the Trends module
    const trendsModule = baseDataset.supported_visualizations.find((v: any) =>
      v.id.includes('viz_trends')
    );

    // 2. Automatically pick the first available trend option
    if (trendsModule && trendsModule.options.length > 0) {
      const defaultOption = trendsModule.options[0];
      void fetchTrends(defaultOption.target_property, 'year');
    }
  }, [baseDataset]);

  if (!baseDataset) {
    return (
      <div className="text-white text-center py-8">
        Select a base dataset in the sidebar to view dashboard.
      </div>
    );
  }

  // Render Logic
  switch (activeTab) {
    case 'graph':
      return <GraphVis />;
    case '3d':
      return <ThreeDGraphVis />;
    case 'compare':
      return <CompareCard />;
    case 'analytics':
    default:
      return (
        <div className="space-y-6">
          {/* Top Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard
              title="Size"
              value={formatSize(baseDataset.size_in_bytes)}
              icon={<Database size={24} />}
              color="cyan"
            />
            <StatCard
              title="Number of Files"
              value={baseDataset.number_of_files?.toLocaleString() || '0'}
              color="emerald"
              icon={<Files size={24} />}
            />
            {/* Hardcoded mocks for demo - could be replaced with real backend aggregations later */}
            <StatCard
              title="Relationships"
              value="18.5K"
              trend="up"
              trendValue={8}
              icon={<Users size={24} />}
              color="amber"
            />
            <StatCard
              title="Growth Rate"
              value="48%"
              trend="up"
              trendValue={24}
              icon={<TrendingUp size={24} />}
              color="rose"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartCard
              title="Bar Chart"
              subtitle="Distribution over Years"
              type="bar"
              data={trendData}
              dataKey="count"
              xKey="label"
            />
            <ChartCard
              title="Line Chart"
              subtitle="Growth over Years"
              type="line"
              data={trendData}
              dataKey="count"
              xKey="label"
            />
          </div>
        </div>
      );
  }
};
