import React, { useEffect, useRef, useState } from 'react';
import { AlertOctagon, AlertTriangle, ChevronRight, Info, Radio, ShieldAlert } from 'lucide-react';
import { Incident } from '../../types';

interface LiveIncidentLogProps {
  incidents: Incident[];
  selectedId?: number;
  activeId?: number;
  isAnalyzing?: boolean;
  onSelect: (incident: Incident) => void;
}

const severityStyle: Record<string, { icon: React.ElementType; badge: string; dot: string }> = {
  CRITICAL: { icon: AlertOctagon, badge: 'border-red-500/60 bg-red-950/60 text-red-200', dot: 'bg-red-500' },
  HIGH: { icon: AlertTriangle, badge: 'border-orange-500/60 bg-orange-950/60 text-orange-200', dot: 'bg-orange-500' },
  MEDIUM: { icon: ShieldAlert, badge: 'border-amber-500/60 bg-amber-950/60 text-amber-100', dot: 'bg-amber-400' },
  LOW: { icon: Info, badge: 'border-sky-500/60 bg-sky-950/60 text-sky-100', dot: 'bg-sky-400' },
  SAFE: { icon: Info, badge: 'border-emerald-500/60 bg-emerald-950/60 text-emerald-100', dot: 'bg-emerald-400' }
};

const eventLabel = (incident: Incident) => incident.display_label || incident.behaviour_name.toUpperCase();

export const LiveIncidentLog: React.FC<LiveIncidentLogProps> = ({ incidents, selectedId, activeId, isAnalyzing, onSelect }) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [newestId, setNewestId] = useState<number | undefined>();
  const ordered = [...incidents].sort((a, b) => a.timestamp_seconds - b.timestamp_seconds);

  useEffect(() => {
    const latest = ordered.at(-1);
    if (!latest) return;
    setNewestId(latest.id);
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [incidents.length]); // Each backend event is intentionally a separate log row.

  return (
    <section className="flex min-h-[360px] flex-col overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-950 shadow-xl shadow-slate-950/40 lg:min-h-0">
      <header className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${isAnalyzing ? 'animate-pulse bg-rose-500' : 'bg-slate-600'}`} />
          <div>
            <h2 className="font-mono text-xs font-bold uppercase tracking-wider text-slate-100">Live incident log</h2>
            <p className="mt-0.5 font-mono text-[10px] text-slate-500">{isAnalyzing ? 'Streaming pipeline events' : 'Recorded analysis events'}</p>
          </div>
        </div>
        <span className="flex items-center gap-1 font-mono text-[10px] text-rose-300"><Radio className="h-3 w-3" />{incidents.length}</span>
      </header>

      <div className="flex-1 divide-y divide-slate-800/70 overflow-y-auto scroll-smooth">
        {!ordered.length ? (
          <div className="flex h-full min-h-[260px] flex-col items-center justify-center px-6 text-center font-mono text-xs text-slate-500">
            <Radio className={`mb-3 h-6 w-6 ${isAnalyzing ? 'animate-pulse text-rose-500' : 'text-slate-700'}`} />
            {isAnalyzing ? 'Listening for detections from the active analysis…' : 'No incidents detected for this video.'}
          </div>
        ) : ordered.map((incident) => {
          const style = severityStyle[incident.risk_level] || severityStyle.MEDIUM;
          const Icon = style.icon;
          const selected = incident.id === selectedId || incident.id === activeId;
          const worker = incident.metadata?.worker?.label;
          return (
            <button key={incident.id} onClick={() => onSelect(incident)} className={`group w-full px-4 py-3 text-left transition hover:bg-slate-900/90 ${selected ? 'bg-slate-900 ring-1 ring-inset ring-rose-500/50' : ''} ${incident.id === newestId ? 'animate-[pulse_900ms_ease-out_1]' : ''}`}>
              <div className="flex items-start gap-2.5">
                <time className="w-11 shrink-0 pt-1 font-mono text-[11px] font-bold tabular-nums text-slate-300">{incident.timestamp}</time>
                <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${style.dot}`} />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="font-mono text-[11px] font-bold tracking-wide text-slate-100">{eventLabel(incident)}</span>
                    <span className={`rounded border px-1.5 py-0.5 font-mono text-[9px] font-bold ${style.badge}`}>{incident.risk_level}</span>
                  </div>
                  <p className="mt-1 font-mono text-[10px] font-semibold text-slate-300">{worker || incident.object_id}</p>
                  <p className="mt-1 line-clamp-2 text-[11px] leading-snug text-slate-500">{incident.evidence?.[0] || 'Behaviour rule triggered by the video analysis pipeline.'}</p>
                </div>
                <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${selected ? 'text-rose-400' : 'text-slate-600 group-hover:text-slate-400'}`} />
                <ChevronRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-700" />
              </div>
            </button>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </section>
  );
};
