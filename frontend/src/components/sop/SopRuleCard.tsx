import React from 'react';
import { SopRule } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { BookOpen, Check, ShieldAlert, Sparkles, AlertTriangle } from 'lucide-react';

export const SopRuleCard: React.FC<{ rule: SopRule; isShowcase?: boolean }> = ({ rule, isShowcase }) => {
  return (
    <div className={`p-5 rounded-xl border transition-all glass-card ${
      isShowcase
        ? 'border-rose-600/40 bg-rose-950/15 shadow-lg shadow-rose-950/20'
        : 'border-slate-800 hover:border-slate-700'
    }`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-700/80 flex items-center justify-center text-rose-400">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-rose-400 font-semibold">{rule.code}</span>
              {isShowcase && (
                <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-rose-600 text-white font-bold tracking-wide">
                  SHOWCASE
                </span>
              )}
            </div>
            <h4 className="text-sm font-bold text-slate-100 tracking-tight mt-0.5">
              {rule.name}
            </h4>
          </div>
        </div>
        <StatusBadge type="risk" value={rule.severity} size="sm" />
      </div>

      <p className="text-xs text-slate-300 leading-relaxed mt-3">
        {rule.description}
      </p>

      {/* Detection Conditions */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
        <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400 block">
          Algorithmic Detection Criteria
        </span>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(rule.conditions || {}).map(([key, val], idx) => (
            <span
              key={idx}
              className="px-2 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300 flex items-center gap-1"
            >
              <Check className="w-3 h-3 text-emerald-400" />
              <span>{key.replace(/_/g, ' ')}: <strong className="text-rose-300">{String(val)}</strong></span>
            </span>
          ))}
        </div>
      </div>

      {/* Recommendation */}
      <div className="mt-3.5 p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs">
        <span className="font-mono text-slate-400 font-semibold block mb-0.5">Mandated Corrective Action:</span>
        <span className="text-slate-200">{rule.recommendation}</span>
      </div>
    </div>
  );
};
