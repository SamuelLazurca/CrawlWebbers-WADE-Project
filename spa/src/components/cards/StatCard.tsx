import React from 'react';
import {Minus, TrendingDown, TrendingUp} from 'lucide-react';
import {cn} from '../../lib/utils';

type ColorType = 'cyan' | 'emerald' | 'amber' | 'rose' | 'purple';

interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  icon?: React.ReactNode;
  color?: ColorType;
  description?: string;
}

const COLOR_STYLES: Record<ColorType, {
  bg: string;
  border: string;
  icon: string;
  accent: string;
  trend: string;
  gradient: string;
}> = {
  cyan: {
    bg: 'from-cyan-500/10 to-blue-500/5',
    border: 'border-cyan-500/20',
    icon: 'text-cyan-400',
    accent: 'bg-cyan-500/20 text-cyan-300',
    trend: 'text-cyan-300',
    gradient: '#06b6d4',
  },
  emerald: {
    bg: 'from-emerald-500/10 to-green-500/5',
    border: 'border-emerald-500/20',
    icon: 'text-emerald-400',
    accent: 'bg-emerald-500/20 text-emerald-300',
    trend: 'text-emerald-300',
    gradient: '#10b981',
  },
  amber: {
    bg: 'from-amber-500/10 to-orange-500/5',
    border: 'border-amber-500/20',
    icon: 'text-amber-400',
    accent: 'bg-amber-500/20 text-amber-300',
    trend: 'text-amber-300',
    gradient: '#f59e0b',
  },
  rose: {
    bg: 'from-rose-500/10 to-pink-500/5',
    border: 'border-rose-500/20',
    icon: 'text-rose-400',
    accent: 'bg-rose-500/20 text-rose-300',
    trend: 'text-rose-300',
    gradient: '#f43f5e',
  },
  purple: {
    bg: 'from-purple-500/10 to-violet-500/5',
    border: 'border-purple-500/20',
    icon: 'text-purple-400',
    accent: 'bg-purple-500/20 text-purple-300',
    trend: 'text-purple-300',
    gradient: '#a855f7',
  },
};

export const StatCard: React.FC<StatCardProps> = (
  {
    title,
    value,
    unit,
    trend,
    trendValue,
    icon,
    color = 'cyan',
    description,
  }) => {
  const styles = COLOR_STYLES[color];

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-2xl p-6',
        'bg-linear-to-br border backdrop-blur-sm',
        'hover:shadow-2xl hover:shadow-slate-900/50 transition-all duration-300',
        'hover:scale-105 hover:-translate-y-1',
        styles.bg,
        styles.border
      )}
    >
      <div
        className="absolute top-0 right-0 w-32 h-32 opacity-20 blur-3xl rounded-full pointer-events-none"
        style={{ background: `linear-gradient(135deg, ${styles.gradient}, transparent)` }}
      />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
            <h3 className="text-3xl font-bold text-white">
              {value}
              {unit && <span className="text-lg text-slate-400 ml-1">{unit}</span>}
            </h3>
          </div>
          {icon && <div className={cn('text-2xl', styles.icon)}>{icon}</div>}
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
          {trend && trendValue !== undefined ? (
            <div className="flex items-center gap-2">
              <div className={cn('p-1 rounded', styles.accent)}>
                {trend === 'up' && <TrendingUp size={14} />}
                {trend === 'down' && <TrendingDown size={14} />}
                {trend === 'stable' && <Minus size={14} />}
              </div>
              <span className={cn('text-sm font-semibold', styles.trend)}>
                {trend === 'up' ? '+' : ''}
                {trendValue}%
              </span>
            </div>
          ) : (
            <div />
          )}
          {description && <p className="text-xs text-slate-400">{description}</p>}
        </div>
      </div>
    </div>
  );
};
