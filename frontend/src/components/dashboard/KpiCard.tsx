import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  label: string;
  value: number | string;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'critical' | 'high' | 'medium' | 'low' | 'success';
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  subtitle,
  icon: Icon,
  variant = 'default'
}) => {
  let borderClass = 'border-slate-800';
  let badgeColor = 'text-slate-400 bg-slate-800/80';
  let valueColor = 'text-slate-100';

  switch (variant) {
    case 'critical':
      borderClass = 'border-rose-600/40 bg-rose-950/20';
      badgeColor = 'text-rose-400 bg-rose-950/60';
      valueColor = 'text-rose-400';
      break;
    case 'high':
      borderClass = 'border-rose-700/30 bg-rose-950/10';
      badgeColor = 'text-rose-400 bg-rose-950/40';
      valueColor = 'text-rose-300';
      break;
    case 'medium':
      borderClass = 'border-amber-600/30 bg-amber-950/10';
      badgeColor = 'text-amber-400 bg-amber-950/40';
      valueColor = 'text-amber-300';
      break;
    case 'low':
      borderClass = 'border-sky-600/30 bg-sky-950/10';
      badgeColor = 'text-sky-400 bg-sky-950/40';
      valueColor = 'text-sky-300';
      break;
    case 'success':
      borderClass = 'border-emerald-600/30 bg-emerald-950/10';
      badgeColor = 'text-emerald-400 bg-emerald-950/40';
      valueColor = 'text-emerald-300';
      break;
  }

  return (
    <div className={`p-4 rounded-xl glass-card border ${borderClass} transition-all hover:border-slate-700`}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-mono font-medium uppercase tracking-wider text-slate-400">{label}</span>
        <div className={`p-2 rounded-lg ${badgeColor}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-2">
        <span className={`text-2xl font-bold font-mono tracking-tight ${valueColor}`}>{value}</span>
        {subtitle && <p className="text-[11px] text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  );
};
