import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {cn} from '../../lib/utils';
import type {RechartsData, TooltipPayloadItem} from "../../types";

interface ChartCardProps<T extends object> {
  title: string;
  subtitle?: string;
  type: 'bar' | 'line' | 'pie';
  data: T[];
  dataKey: keyof T;
  xKey?: keyof T;
  height?: number;
  colors?: string[];
  onClick?: () => void;
  headerAction?: React.ReactNode;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string;
}

const DEFAULT_COLORS = ['#0ea5e9', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className='bg-slate-950/95 border border-slate-700 rounded-lg p-3 shadow-xl backdrop-blur-md'>
        <p className='text-sm font-semibold text-white'>{label}</p>
        <p className='text-sm text-emerald-400'>
          {payload[0].name}: {payload[0].value}
        </p>
      </div>
    );
  }
  return null;
};

export const ChartCard = <T extends object>({
  title,
  subtitle,
  type,
  data,
  dataKey,
  xKey = 'label' as keyof T,
  height = 300,
  colors = DEFAULT_COLORS,
  onClick,
  headerAction,
}: ChartCardProps<T>) => {
  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-2xl p-6',
        'bg-linear-to-br from-slate-800/30 to-slate-900/20',
        'border border-slate-700/50 backdrop-blur-sm',
        onClick &&
          'cursor-pointer hover:shadow-xl hover:scale-105 hover:-translate-y-1 transition-all duration-300'
      )}
    >
      <div className='mb-6 flex justify-between items-start'>
        <div>
          <h3 className='text-lg font-bold text-white'>{title}</h3>
          {subtitle && (
            <p className='text-sm text-slate-400 mt-1'>{subtitle}</p>
          )}
        </div>
        {headerAction && <div className='z-20'>{headerAction}</div>}
      </div>

      <ResponsiveContainer width='100%' height={height}>
        {type === 'pie' ? (
          <PieChart>
            <Pie
              data={data as RechartsData[]}
              dataKey={dataKey as string}
              nameKey={xKey as string}
              cx='50%'
              cy='50%'
              outerRadius={80}
              animationDuration={800}
            >
              {data.map((_, idx) => (
                <Cell key={`cell-${idx}`} fill={colors[idx % colors.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        ) : type === 'bar' ? (
          <BarChart
            data={data as RechartsData[]}
            margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
          >
            <CartesianGrid
              strokeDasharray='3 3'
              stroke='#334155'
              opacity={0.3}
            />
            <XAxis
              dataKey={xKey as string}
              stroke='#94a3b8'
              style={{ fontSize: 12 }}
              axisLine={false}
            />
            <YAxis stroke='#94a3b8' style={{ fontSize: 12 }} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey={dataKey as string}
              fill={colors[0]}
              radius={[8, 8, 0, 0]}
              animationDuration={800}
            />
          </BarChart>
        ) : (
          <LineChart
            data={data as RechartsData[]}
            margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
          >
            <CartesianGrid
              strokeDasharray='3 3'
              stroke='#334155'
              opacity={0.3}
            />
            <XAxis
              dataKey={xKey as string}
              stroke='#94a3b8'
              style={{ fontSize: 12 }}
              axisLine={false}
            />
            <YAxis stroke='#94a3b8' style={{ fontSize: 12 }} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type='monotone'
              dataKey={dataKey as string}
              stroke={colors[0]}
              strokeWidth={3}
              dot={false}
              animationDuration={800}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};
