import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { useSystemHealth } from '../api/system';
import { useWarehouseZones } from '../api/sop';
import { StatusBadge } from '../components/common/StatusBadge';
import { Server, Cpu, RotateCcw, MapPin } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { data: health, refetch: refetchHealth } = useSystemHealth();
  const { data: zones } = useWarehouseZones();
  const confThresh = health?.confidence_threshold ?? 0.35;

  return (
    <PageContainer
      title="SYSTEM SETTINGS & DIAGNOSTICS"
      subtitle="Operational engine status, threshold parameters, hardware acceleration, and zone configurations."
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* System Health Status */}
        <div className="lg:col-span-6 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <Server className="w-4 h-4 text-rose-500" />
              Operational Health Matrix
            </h3>
            <button
              onClick={() => refetchHealth()}
              className="text-xs font-mono text-rose-400 hover:text-rose-300 flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-slate-300">FastAPI Backend:</span>
              <StatusBadge type="system" value={health?.backend || 'UNHEALTHY'} size="sm" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-slate-300">SQLite Database:</span>
              <StatusBadge type="system" value={health?.database || 'UNHEALTHY'} size="sm" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-slate-300">Ollama LLM Engine:</span>
              <StatusBadge type="system" value={health?.ollama || 'OFFLINE'} size="sm" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-slate-300">Vision Model (YOLO):</span>
              <StatusBadge type="system" value={health?.vision_model || 'LOADED'} size="sm" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <span className="text-slate-300">FFmpeg Video Transcoder:</span>
              <StatusBadge type="system" value={health?.ffmpeg || 'UNAVAILABLE'} size="sm" />
            </div>
          </div>
        </div>

        {/* Perception Sensitivity Configuration */}
        <div className="lg:col-span-6 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            Perception Engine Parameters
          </h3>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <div className="flex justify-between text-slate-300 mb-1.5">
                <span>Confidence Threshold:</span>
                <span className="text-rose-400 font-bold">{confThresh}</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-lg bg-slate-800">
                <div className="h-full rounded-lg bg-rose-500" style={{ width: `${confThresh * 100}%` }} />
              </div>
              <p className="text-[11px] text-slate-500 mt-1 font-sans">
                Read from `CONFIDENCE_THRESHOLD` in backend configuration. Restart the backend after changing `.env`.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
              <span className="text-slate-400 block">Active Local Model:</span>
              <span className="text-cyan-300 font-bold">{health?.active_model || 'qwen2.5:3b'}</span>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
              <span className="text-slate-400 block">Incident Replay Window:</span>
              <span className="text-slate-200 font-bold">{health?.clip_pre_seconds ?? 3.0}s pre-incident + duration + {health?.clip_post_seconds ?? 3.0}s post-incident</span>
            </div>
          </div>
        </div>

        {/* Configured Warehouse Polygon Zones */}
        <div className="lg:col-span-12 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-400" />
            Active Warehouse Operational Zones
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {zones && zones.map((z: any, idx: number) => (
              <div key={idx} className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold font-mono text-slate-200">{z.name}</span>
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: z.color || '#3b82f6' }} />
                </div>
                <p className="text-[11px] text-slate-400 font-sans">{z.description}</p>
                <div className="text-[10px] font-mono text-slate-500">
                  Polygon points: {z.polygon ? z.polygon.length : 4} vertices
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
};
