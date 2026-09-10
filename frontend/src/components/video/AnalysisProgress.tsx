import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, CheckCircle, Flame, Sparkles } from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';

interface AnalysisProgressProps {
  jobId: string;
  onComplete?: () => void;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ jobId, onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Initializing perception model and frame buffer...');
  const [recentAlert, setRecentAlert] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const { updateAnalysisProgress, setAnalysisState } = useAppStore();

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/analysis/${jobId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to analysis WebSocket:', jobId);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'progress') {
          setProgress(data.percentage);
          setMessage(data.message || `Processing frame ${data.frame}/${data.total_frames}`);
          updateAnalysisProgress(data.percentage, data.message || '');
        } else if (data.type === 'incident_detected') {
          const incident = data.incident;
          if (incident) {
            setRecentAlert(`FLAGGED: ${incident.display_label || incident.behaviour_name} on ${incident.metadata?.worker?.label || incident.object_id} (${incident.risk_level})`);
          }
        } else if (data.type === 'completed') {
          setProgress(100);
          setMessage(data.message || 'Analysis successfully completed!');
          setIsCompleted(true);
          setAnalysisState(false, null, 100, 'Analysis completed');
          if (onComplete) onComplete();
        } else if (data.type === 'error') {
          setMessage(data.message || 'Analysis failed. Check system health and try again.');
          setIsFailed(true);
          setAnalysisState(false, null, progress, 'Analysis failed');
        }
      } catch (err) {
        console.error('WebSocket parse error:', err);
      }
    };

    ws.onerror = (err) => {
      console.warn('WebSocket error, falling back to polling:', err);
    };

    return () => {
      ws.close();
    };
  }, [jobId]);

  return (
    <div className="p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-rose-500 animate-pulse" />
          <h4 className="text-sm font-semibold text-slate-100 font-mono">
            {isFailed ? 'ANALYSIS FAILED' : isCompleted ? 'ANALYSIS COMPLETED' : 'ACTIVE PIPELINE ANALYSIS'}
          </h4>
        </div>
        <span className="text-xs font-mono font-bold text-rose-400">
          {progress}%
        </span>
      </div>

      {/* Animated Progress Bar */}
      <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden p-0.5 border border-slate-800">
        <div
          className="bg-gradient-to-r from-rose-600 via-rose-500 to-amber-500 h-full rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs font-mono text-slate-400">
        <span className="flex items-center gap-1.5 truncate max-w-[80%]">
          <Sparkles className="w-3.5 h-3.5 text-rose-400 shrink-0" />
          <span>{message}</span>
        </span>
        <span className="text-[11px] text-slate-500 shrink-0">JOB: {jobId.slice(0, 8)}</span>
      </div>

      {/* Live Incident Trigger Banner */}
      {recentAlert && (
        <div className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-700/60 text-xs font-mono text-rose-300 flex items-center gap-2 animate-bounce">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span className="font-semibold">{recentAlert}</span>
        </div>
      )}
    </div>
  );
};
