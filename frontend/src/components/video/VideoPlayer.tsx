import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertOctagon, AlertTriangle, Info, Pause, Play, Radio, RotateCcw, ShieldAlert, Sparkles, Volume2, VolumeX } from 'lucide-react';
import { FrameObservation, Incident, TrackedObjectSnapshot, Video } from '../../types';
import { useAppStore } from '../../stores/useAppStore';
import { BACKEND_BASE } from '../../api/client';

interface VideoPlayerProps {
  video: Video;
  incidents: Incident[];
  observations?: FrameObservation[];
  seekTime?: number;
  onSelectIncident?: (incident: Incident) => void;
  onActiveIncident?: (incident: Incident) => void;
}

const RISK: Record<string, { badge: string; stroke: string; icon: React.ElementType }> = {
  CRITICAL: { badge: 'bg-red-950/90 text-red-200 border-red-500/70', stroke: '#ef4444', icon: AlertOctagon },
  HIGH: { badge: 'bg-orange-950/90 text-orange-200 border-orange-500/70', stroke: '#f97316', icon: AlertTriangle },
  MEDIUM: { badge: 'bg-amber-950/90 text-amber-100 border-amber-500/70', stroke: '#f59e0b', icon: ShieldAlert },
  LOW: { badge: 'bg-sky-950/90 text-sky-100 border-sky-500/70', stroke: '#38bdf8', icon: Info },
  SAFE: { badge: 'bg-emerald-950/90 text-emerald-100 border-emerald-500/70', stroke: '#34d399', icon: Info }
};

const labelFor = (incident: Incident) => incident.display_label || ({
  DROP_PRODUCT: 'POSSIBLE DROP',
  DRAG_PRODUCT: 'DRAGGING DETECTED',
  PALLET_OVERHANG: 'PALLET OVERHANG',
  IMPROPER_STAGING: 'IMPROPER STAGING',
  STACK_ORDER: 'IMPROPER STACKING'
}[incident.behaviour] || incident.behaviour_name.toUpperCase());

const fmt = (seconds: number) => `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`;

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ video, incidents, observations = [], seekTime, onSelectIncident, onActiveIncident }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const activeIdRef = useRef<number | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(video.duration || 0);
  const [isMuted, setIsMuted] = useState(true);
  const [showProcessed, setShowProcessed] = useState(Boolean(video.processed_path));
  const [intrinsicSize, setIntrinsicSize] = useState({ width: video.width, height: video.height });
  const { setCurrentPlaybackTime } = useAppStore();

  const orderedIncidents = [...incidents].sort((a, b) => a.timestamp_seconds - b.timestamp_seconds);
  const activeIncident = [...orderedIncidents].reverse().find((incident) => (
    currentTime >= incident.timestamp_seconds - 0.25
      && currentTime <= incident.timestamp_seconds + Math.max(2.5, incident.duration || 0)
  ));
  const closestObservation = observations.reduce<FrameObservation | undefined>((closest, observation) => {
    if (Math.abs(observation.timestamp_seconds - currentTime) > 0.6) return closest;
    if (!closest || Math.abs(observation.timestamp_seconds - currentTime) < Math.abs(closest.timestamp_seconds - currentTime)) return observation;
    return closest;
  }, undefined);
  const visibleTracks = closestObservation?.tracks || activeIncident?.metadata?.tracks || [];
  const sourceUrl = showProcessed && video.processed_path
    ? `${BACKEND_BASE}/storage/processed/${video.processed_path.split(/[/\\]/).pop()}`
    : `${BACKEND_BASE}/storage/uploads/${video.filename}`;

  useEffect(() => {
    setShowProcessed(Boolean(video.processed_path));
    setCurrentTime(0);
    setDuration(video.duration || 0);
    activeIdRef.current = null;
  }, [video.id, video.processed_path, video.duration]);

  useEffect(() => {
    if (seekTime === undefined || !videoRef.current) return;
    videoRef.current.currentTime = seekTime;
    setCurrentTime(seekTime);
    setCurrentPlaybackTime(seekTime);
    void videoRef.current.play().then(() => setIsPlaying(true)).catch(() => undefined);
  }, [seekTime, setCurrentPlaybackTime]);

  useEffect(() => {
    if (!activeIncident || activeIncident.id === activeIdRef.current) return;
    activeIdRef.current = activeIncident.id;
    onActiveIncident?.(activeIncident);
  }, [activeIncident, onActiveIncident]);

  const drawTrackedObject = (ctx: CanvasRenderingContext2D, track: TrackedObjectSnapshot, color: string, emphasis = false, annotation?: string) => {
    const [x1, y1, x2, y2] = track.bbox;
    const x = x1 * ctx.canvas.width;
    const y = y1 * ctx.canvas.height;
    const width = (x2 - x1) * ctx.canvas.width;
    const height = (y2 - y1) * ctx.canvas.height;
    ctx.strokeStyle = color;
    ctx.fillStyle = emphasis ? `${color}22` : 'transparent';
    ctx.lineWidth = emphasis ? 5 : 2;
    ctx.strokeRect(x, y, width, height);
    if (emphasis) ctx.fillRect(x, y, width, height);
    const text = annotation ? `${track.label} · ${annotation}` : track.label;
    ctx.font = `${emphasis ? 15 : 13}px ui-monospace, SFMono-Regular, Menlo, monospace`;
    const textWidth = ctx.measureText(text).width;
    const textY = Math.max(22, y - 5);
    ctx.fillStyle = color;
    ctx.fillRect(x, textY - 19, textWidth + 12, 23);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(text, x + 6, textY - 4);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const width = intrinsicSize.width || video.width;
    const height = intrinsicSize.height || video.height;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);
    visibleTracks.forEach((track) => drawTrackedObject(ctx, track, track.class_name === 'person' ? '#38bdf8' : '#4ade80'));
    if (!activeIncident?.metadata) return;
    const risk = RISK[activeIncident.risk_level] || RISK.MEDIUM;
    const targets = [
      activeIncident.metadata.subject,
      activeIncident.metadata.worker || undefined,
      ...(activeIncident.metadata.related_objects || [])
    ].filter(Boolean) as TrackedObjectSnapshot[];
    targets.forEach((track, index) => drawTrackedObject(ctx, track, risk.stroke, true, index === 0 ? labelFor(activeIncident) : 'RELATED'));
  }, [activeIncident, intrinsicSize, video.height, video.width, visibleTracks]);

  const updateTime = () => {
    const time = videoRef.current?.currentTime || 0;
    setCurrentTime(time);
    setCurrentPlaybackTime(time);
  };
  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) void videoRef.current.play().then(() => setIsPlaying(true)).catch(() => undefined);
    else { videoRef.current.pause(); setIsPlaying(false); }
  };
  const seek = (time: number) => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = time;
    setCurrentTime(time);
    setCurrentPlaybackTime(time);
  };
  const selectFromTimeline = useCallback((incident: Incident) => {
    seek(incident.timestamp_seconds);
    onSelectIncident?.(incident);
    void videoRef.current?.play().then(() => setIsPlaying(true)).catch(() => undefined);
  }, [onSelectIncident]);

  const activeRisk = activeIncident ? (RISK[activeIncident.risk_level] || RISK.MEDIUM) : null;
  const ActiveIcon = activeRisk?.icon || Info;

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-700/80 bg-black shadow-2xl shadow-slate-950/70">
      <div className="relative aspect-video w-full bg-slate-950">
        <video
          ref={videoRef}
          src={sourceUrl}
          muted={isMuted}
          playsInline
          className="h-full w-full cursor-pointer object-contain"
          onClick={togglePlay}
          onTimeUpdate={updateTime}
          onLoadedMetadata={() => {
            if (!videoRef.current) return;
            setDuration(videoRef.current.duration || video.duration);
            setIntrinsicSize({ width: videoRef.current.videoWidth || video.width, height: videoRef.current.videoHeight || video.height });
          }}
          onEnded={() => setIsPlaying(false)}
        />
        {/* This canvas consumes detector snapshots from the analysis websocket. */}
        <canvas ref={canvasRef} className="pointer-events-none absolute inset-0 h-full w-full object-contain" aria-label="Live AI detection overlays" />

        {!isPlaying && (
          <button onClick={togglePlay} aria-label="Play video" className="absolute inset-0 m-auto flex h-16 w-16 items-center justify-center rounded-full bg-rose-600/90 text-white shadow-xl shadow-rose-950/60 transition hover:scale-110 hover:bg-rose-500">
            <Play className="ml-1 h-8 w-8" />
          </button>
        )}
        <div className="pointer-events-none absolute left-3 right-3 top-3 flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 rounded-md border border-slate-700/70 bg-black/75 px-2.5 py-1 font-mono text-[11px] text-slate-200 backdrop-blur">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            <span className="max-w-[180px] truncate">{video.original_name}</span>
            <span className="text-slate-500">{Math.round(video.fps)} FPS</span>
          </div>
          {video.processed_path && (
            <button onClick={() => setShowProcessed((value) => !value)} className="pointer-events-auto flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900/90 px-3 py-1 font-mono text-[11px] font-semibold text-slate-200 backdrop-blur transition hover:bg-slate-800">
              <Sparkles className="h-3.5 w-3.5 text-rose-400" />
              {showProcessed ? 'ANNOTATED REPLAY' : 'LIVE OVERLAY'}
            </button>
          )}
        </div>

        {activeIncident && activeRisk && (
          <div className={`absolute bottom-3 left-3 flex max-w-[90%] items-start gap-2 rounded-lg border px-3 py-2 shadow-xl backdrop-blur ${activeRisk.badge} animate-pulse`}>
            <ActiveIcon className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="font-mono text-[11px] leading-snug">
              <strong className="tracking-wide">{labelFor(activeIncident)}</strong>
              <span className="ml-2 opacity-80">{activeIncident.metadata?.worker?.label || activeIncident.object_id}</span>
              <div className="mt-0.5 opacity-75">{activeIncident.evidence?.[0] || 'Backend behaviour rule triggered'}</div>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-2 border-t border-slate-800 bg-slate-900/95 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="w-10 font-mono text-[11px] tabular-nums text-slate-300">{fmt(currentTime)}</span>
          <div className="relative flex h-4 flex-1 items-center">
            <input type="range" min="0" max={duration || 1} step="0.05" value={Math.min(currentTime, duration || currentTime)} onChange={(event) => seek(Number(event.target.value))} className="absolute z-10 h-1.5 w-full cursor-pointer appearance-none rounded-lg bg-slate-700 accent-rose-500" />
            {duration > 0 && orderedIncidents.map((incident) => (
              <button key={incident.id} onClick={() => selectFromTimeline(incident)} title={`${fmt(incident.timestamp_seconds)} — ${labelFor(incident)}`} style={{ left: `${Math.min(100, (incident.timestamp_seconds / duration) * 100)}%` }} className="absolute -top-0.5 z-20 h-3 w-3 -translate-x-1/2 rounded-full border-2 border-slate-950 bg-rose-500 transition hover:scale-150" />
            ))}
          </div>
          <span className="w-10 font-mono text-[11px] tabular-nums text-slate-500">{fmt(duration)}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1">
            <button onClick={togglePlay} aria-label="Play or pause" className="rounded-md p-1.5 text-slate-300 transition hover:bg-slate-800 hover:text-white">{isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}</button>
            <button onClick={() => seek(0)} aria-label="Restart" className="rounded-md p-1.5 text-slate-300 transition hover:bg-slate-800 hover:text-white"><RotateCcw className="h-4 w-4" /></button>
            <button onClick={() => setIsMuted((value) => !value)} aria-label="Toggle audio" className="rounded-md p-1.5 text-slate-300 transition hover:bg-slate-800 hover:text-white">{isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}</button>
          </div>
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-rose-300"><Radio className="h-3.5 w-3.5 animate-pulse" />{incidents.length} backend events</span>
        </div>
      </div>
    </div>
  );
};
