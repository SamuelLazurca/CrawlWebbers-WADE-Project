import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { cn } from '../../lib/utils';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  type: 'bar' | 'line' | 'pie';
  data: any[];
  dataKey: string;
  xKey?: string;
  height?: number;
  colors?: string[];
  onClick?: () => void;
}

// Define a simple interface to avoid Recharts type conflicts
interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

const DEFAULT_COLORS = ['#0ea5e9', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-950/95 border border-slate-700 rounded-lg p-3 shadow-xl backdrop-blur-md">
        <p className="text-sm font-semibold text-white">{label}</p>
        <p className="text-sm text-emerald-400">
          {payload[0].name}: {payload[0].value}
        </p>
      </div>
    );
  }
  return null;
};

export const ChartCard: React.FC<ChartCardProps> = ({
                                                      title,
                                                      subtitle,
                                                      type,
                                                      data,
                                                      dataKey,
                                                      xKey = 'label',
                                                      height = 300,
                                                      colors = DEFAULT_COLORS,
                                                      onClick,
                                                    }) => {
  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-2xl p-6',
        'bg-gradient-to-br from-slate-800/30 to-slate-900/20',
        'border border-slate-700/50 backdrop-blur-sm',
        onClick && 'cursor-pointer hover:shadow-xl hover:scale-105 hover:-translate-y-1 transition-all duration-300'
      )}
    >
      <div className="mb-6">
        <h3 className="text-lg font-bold text-white">{title}</h3>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>

      <ResponsiveContainer width="100%" height={height}>
        {type === 'pie' ? (
          <PieChart>
            <Pie
              data={data}
              dataKey={dataKey}
              nameKey={xKey}
              cx="50%"
              cy="50%"
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
          <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
            <XAxis dataKey={xKey} stroke="#94a3b8" style={{ fontSize: 12 }} axisLine={false} />
            <YAxis stroke="#94a3b8" style={{ fontSize: 12 }} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey={dataKey} fill={colors[0]} radius={[8, 8, 0, 0]} animationDuration={800} />
          </BarChart>
        ) : (
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
            <XAxis dataKey={xKey} stroke="#94a3b8" style={{ fontSize: 12 }} axisLine={false} />
            <YAxis stroke="#94a3b8" style={{ fontSize: 12 }} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey={dataKey}
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