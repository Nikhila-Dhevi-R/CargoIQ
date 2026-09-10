import React from 'react';
import { RiskLevel, ReviewStatus } from '../../types';

interface StatusBadgeProps {
  type: 'risk' | 'review' | 'system';
  value: RiskLevel | ReviewStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, value, size = 'md' }) => {
  const v = String(value).toUpperCase();

  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (type === 'risk') {
    switch (v) {
      case 'CRITICAL':
        colorClasses = 'bg-rose-950/80 text-rose-400 border-rose-600/50 glow-critical';
        break;
      case 'HIGH':
        colorClasses = 'bg-rose-950/50 text-rose-400 border-rose-700/40';
        break;
      case 'MEDIUM':
        colorClasses = 'bg-amber-950/50 text-amber-400 border-amber-600/40';
        break;
      case 'LOW':
        colorClasses = 'bg-sky-950/50 text-sky-400 border-sky-600/40';
        break;
      case 'SAFE':
        colorClasses = 'bg-emerald-950/50 text-emerald-400 border-emerald-600/40';
        break;
    }
  } else if (type === 'review') {
    switch (v) {
      case 'REVIEWED':
        colorClasses = 'bg-emerald-950/50 text-emerald-400 border-emerald-600/40';
        break;
      case 'DISMISSED':
        colorClasses = 'bg-slate-800/80 text-slate-400 border-slate-700';
        break;
      case 'UNREVIEWED':
      default:
        colorClasses = 'bg-amber-950/40 text-amber-300 border-amber-600/40';
        break;
    }
  } else if (type === 'system') {
    if (v === 'HEALTHY' || v === 'LOADED' || v === 'AVAILABLE') {
      colorClasses = 'bg-emerald-950/40 text-emerald-400 border-emerald-600/30';
    } else {
      colorClasses = 'bg-rose-950/40 text-rose-400 border-rose-600/30';
    }
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : size === 'lg' ? 'px-3 py-1.5 text-sm font-semibold' : 'px-2.5 py-1 text-xs font-medium';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border font-mono uppercase tracking-wider ${sizeClasses} ${colorClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {v}
    </span>
  );
};
