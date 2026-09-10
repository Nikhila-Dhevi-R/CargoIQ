import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { useSopRules } from '../api/sop';
import { SopRuleCard } from '../components/sop/SopRuleCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { BookOpenCheck, Sparkles, FileCode } from 'lucide-react';
import { SopRule } from '../types';

const SHOWCASE_CODES = [
  'DROP_PRODUCT',
  'DRAG_PRODUCT',
  'PALLET_OVERHANG',
  'IMPROPER_STAGING',
  'STACK_ORDER'
];

export const SopPage: React.FC = () => {
  const { data: rules, isLoading } = useSopRules();

  if (isLoading || !rules) {
    return (
      <PageContainer title="SOP-AS-CODE RULES DIRECTORY">
        <LoadingSpinner label="Loading declarative SOP rule catalogue..." />
      </PageContainer>
    );
  }

  const showcaseRules = rules.filter((r: SopRule) => SHOWCASE_CODES.includes(r.code));
  const otherRules = rules.filter((r: SopRule) => !SHOWCASE_CODES.includes(r.code));

  return (
    <PageContainer
      title="SOP-AS-CODE: 10 WAREHOUSE BEHAVIOURAL RULES"
      subtitle="Declarative standard operating procedure modules loaded dynamically from YAML without retraining machine learning weights."
    >
      {/* Overview Banner */}
      <div className="p-5 rounded-xl glass-panel border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-rose-500" />
            <h3 className="text-sm font-bold font-mono text-slate-100">
              CONFIGURABLE BEHAVIOURAL RULES (godrej_rules.yaml)
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            Rules can be updated, tuned, or extended on-the-fly without rebuilding computer vision models.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
          <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
            10 Active Modules
          </span>
          <span className="px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-800/40 text-rose-300 font-semibold">
            5 Showcase Scenarios
          </span>
        </div>
      </div>

      {/* 5 Showcase Scenarios */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-rose-500" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Primary Showcase Scenarios
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {showcaseRules.map((rule: SopRule) => (
            <SopRuleCard key={rule.code} rule={rule} isShowcase />
          ))}
        </div>
      </div>

      {/* Other 5 Behaviour Modules */}
      <div className="space-y-3 pt-4 border-t border-slate-800/80">
        <div className="flex items-center gap-2">
          <BookOpenCheck className="w-4 h-4 text-slate-400" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
            Additional Handling Compliance Modules
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {otherRules.map((rule: SopRule) => (
            <SopRuleCard key={rule.code} rule={rule} />
          ))}
        </div>
      </div>
    </PageContainer>
  );
};
