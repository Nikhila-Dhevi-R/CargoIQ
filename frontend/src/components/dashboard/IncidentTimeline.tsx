import React from 'react';
import { Incident } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { Clock, PlayCircle, Eye, AlertOctagon } from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';

interface IncidentTimelineProps {
  incidents: Incident[];
  onSelectIncident: (incident: Incident) => void;
  selectedId?: number;
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({
  incidents,
  onSelectIncident,
  selectedId
}) => {
  const { currentPlaybackTime } = useAppStore();

  if (!incidents || incidents.length === 0) {
    return (
      <div className="p-8 text-center glass-panel rounded-xl border border-slate-800 text-slate-400 font-mono text-xs">
        <AlertOctagon className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        No handling anomalies detected in this video feed.
      </div>
    );
  }

  return (
    <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
      {incidents.map((inc) => {
        const isSelected = selectedId === inc.id;
        const isNearPlayback = Math.abs(currentPlaybackTime - inc.timestamp_seconds) < 2.0;

        return (
          <div
            key={inc.id}
            onClick={() => onSelectIncident(inc)}
            className={`cursor-pointer p-3.5 rounded-xl border transition-all ${
              isSelected
                ? 'bg-rose-950/40 border-rose-500/70 shadow-md shadow-rose-950/40'
                : isNearPlayback
                ? 'bg-slate-900 border-amber-500/40'
                : 'glass-card border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60'
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
                <Clock className="w-3.5 h-3.5 text-rose-500" />
                <span className="font-semibold text-slate-100">{inc.timestamp}</span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-400 font-sans">{inc.zone}</span>
              </div>
              <StatusBadge type="risk" value={inc.risk_level} size="sm" />
            </div>

            <div className="mt-2 flex items-center justify-between">
              <div>
                <h4 className="text-sm font-semibold text-slate-100 tracking-tight">
                  {inc.behaviour_name}
                </h4>
                <p className="text-xs font-mono text-slate-400 mt-0.5">
                  Target: <span className="text-rose-300">{inc.object_id}</span>
                </p>
              </div>

              <div className="text-right">
                <div className="text-base font-bold font-mono text-rose-400">
                  {inc.risk_score}<span className="text-[10px] text-slate-500">/100</span>
                </div>
              </div>
            </div>

            {/* Quick footer with replay indicator */}
            <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span className="flex items-center gap-1 text-slate-400 hover:text-slate-200">
                <PlayCircle className="w-3 h-3 text-rose-400" />
                <span>Seek & Inspect</span>
              </span>
              <span className={`text-[10px] uppercase font-semibold ${inc.review_status === 'REVIEWED' ? 'text-emerald-400' : 'text-amber-400'}`}>
                {inc.review_status}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
