import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, AlertOctagon, AlertTriangle, ArrowRight, ShieldAlert, Sparkles, Video as VideoIcon } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { KpiCard } from '../components/dashboard/KpiCard';
import { IncidentDetails } from '../components/incidents/IncidentDetails';
import { LiveIncidentLog } from '../components/video/LiveIncidentLog';
import { VideoPlayer } from '../components/video/VideoPlayer';
import { useAnalyticsOverview } from '../api/analytics';
import { useVideoAnalysisStatus, useVideoEvents, useVideos } from '../api/videos';
import { useAppStore } from '../stores/useAppStore';
import { WEBSOCKET_BASE } from '../api/client';
import { FrameObservation, Incident, Video } from '../types';

const mergeEvents = (persisted: Incident[], streamed: Incident[]) => {
  const byId = new Map<number, Incident>();
  [...persisted, ...streamed].forEach((incident) => byId.set(incident.id, incident));
  return [...byId.values()].sort((a, b) => a.timestamp_seconds - b.timestamp_seconds);
};

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: analytics } = useAnalyticsOverview();
  const { data: videos = [] } = useVideos();
  const { selectedIncident, setSelectedIncident } = useAppStore();
  const [activeVideoIndex, setActiveVideoIndex] = useState(0);
  const [seekTime, setSeekTime] = useState<number | undefined>();
  const [streamedEvents, setStreamedEvents] = useState<Incident[]>([]);
  const [observations, setObservations] = useState<FrameObservation[]>([]);
  const activeVideo: Video | undefined = videos[activeVideoIndex];
  const { data: persistedEvents = [], refetch: refetchEvents } = useVideoEvents(activeVideo?.id);
  const { data: analysisStatus } = useVideoAnalysisStatus(activeVideo?.id);
  const activeJob = analysisStatus?.latest_job;
  const isAnalyzing = activeJob?.status === 'queued' || activeJob?.status === 'processing';
  const incidents = useMemo(() => mergeEvents(persistedEvents, streamedEvents), [persistedEvents, streamedEvents]);

  useEffect(() => {
    setStreamedEvents([]);
    setObservations([]);
    setSeekTime(undefined);
  }, [activeVideo?.id]);

  useEffect(() => {
    if (!activeVideo || !activeJob?.job_id || !isAnalyzing) return;
    const socket = new WebSocket(`${WEBSOCKET_BASE}/ws/analysis/${activeJob.job_id}`);
    socket.onmessage = (message) => {
      const data = JSON.parse(message.data);
      if (data.type === 'incident_detected' && data.incident?.video_id === activeVideo.id) {
        // Do not coalesce: every backend event, including repeated behaviour, is retained.
        setStreamedEvents((current) => current.some((event) => event.id === data.incident.id) ? current : [...current, data.incident]);
      }
      if (data.type === 'frame_observation' && data.video_id === activeVideo.id) {
        setObservations((current) => [...current.filter((observation) => observation.frame !== data.frame), data].slice(-360));
      }
      if (data.type === 'completed' || data.type === 'error') void refetchEvents();
    };
    return () => socket.close();
  }, [activeJob?.job_id, activeVideo?.id, isAnalyzing, refetchEvents]);

  const selectIncident = (incident: Incident) => {
    setSelectedIncident(incident);
    setSeekTime(incident.timestamp_seconds);
  };
  const syncActiveIncident = (incident: Incident) => setSelectedIncident(incident);
  const kpis = analytics?.kpis;

  return (
    <PageContainer
      title="WAREHOUSE VIDEO INTELLIGENCE"
      subtitle="Live worker and cargo tracking with explainable SOP-risk detection."
      action={<button onClick={() => navigate('/analyse')} className="flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 font-mono text-xs font-semibold text-white shadow-lg shadow-rose-950/50 transition hover:scale-105 hover:bg-rose-500"><Sparkles className="h-4 w-4" />ANALYSE VIDEO FEED</button>}
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <KpiCard label="Videos analysed" value={kpis?.total_videos_analysed ?? 0} subtitle="Processed feeds" icon={VideoIcon} />
        <KpiCard label="Live events" value={incidents.length} subtitle="This camera feed" icon={Activity} variant="high" />
        <KpiCard label="Critical" value={incidents.filter((incident) => incident.risk_level === 'CRITICAL').length} subtitle="Immediate hazards" icon={AlertOctagon} variant="critical" />
        <KpiCard label="High risk" value={incidents.filter((incident) => incident.risk_level === 'HIGH').length} subtitle="Supervisor action" icon={AlertTriangle} variant="high" />
      </div>

      <div className="mt-6">
        <div className="mb-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${isAnalyzing ? 'animate-pulse bg-rose-500' : 'bg-emerald-500'}`} />
            <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-slate-100">Warehouse video & live detections</h2>
          </div>
          {videos.length > 1 && <select value={activeVideoIndex} onChange={(event) => setActiveVideoIndex(Number(event.target.value))} className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 font-mono text-xs text-slate-200 focus:outline-none">{videos.map((video, index) => <option key={video.id} value={index}>Feed #{video.id}: {video.original_name}</option>)}</select>}
        </div>

        {activeVideo ? (
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.8fr)_minmax(320px,0.8fr)] xl:items-stretch">
            <VideoPlayer video={activeVideo} incidents={incidents} observations={observations} seekTime={seekTime} onSelectIncident={selectIncident} onActiveIncident={syncActiveIncident} />
            <LiveIncidentLog incidents={incidents} selectedId={selectedIncident?.video_id === activeVideo.id ? selectedIncident.id : undefined} activeId={selectedIncident?.video_id === activeVideo.id ? selectedIncident.id : undefined} isAnalyzing={isAnalyzing} onSelect={selectIncident} />
          </div>
        ) : (
          <div className="flex aspect-video flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-950 p-6 text-center font-mono text-xs text-slate-500"><VideoIcon className="mb-2 h-10 w-10 text-slate-700" />No video feeds ingested. Upload a warehouse video to begin analysis.</div>
        )}
      </div>

      <div className="mt-5 grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="rounded-xl border border-slate-800 bg-slate-900/45 p-4">
          <div className="flex items-center justify-between">
            <div><h3 className="font-mono text-xs font-bold uppercase tracking-wider text-slate-200">Synchronized review</h3><p className="mt-1 text-xs text-slate-500">Click any incident to seek the exact video timestamp. Playback selects the matching event and evidence automatically.</p></div>
            <button onClick={() => navigate('/incidents')} className="flex shrink-0 items-center gap-1 font-mono text-xs text-rose-400 hover:text-rose-300">VIEW ALL <ArrowRight className="h-3.5 w-3.5" /></button>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2 text-center font-mono text-[10px] sm:grid-cols-5">
            <span className="rounded-md border border-slate-800 bg-slate-950 px-2 py-2 text-orange-300">DRAGGING</span>
            <span className="rounded-md border border-slate-800 bg-slate-950 px-2 py-2 text-red-300">POSSIBLE DROP</span>
            <span className="rounded-md border border-slate-800 bg-slate-950 px-2 py-2 text-amber-200">STACKING</span>
            <span className="rounded-md border border-slate-800 bg-slate-950 px-2 py-2 text-orange-300">OVERHANG</span>
            <span className="rounded-md border border-slate-800 bg-slate-950 px-2 py-2 text-sky-300">STAGING</span>
          </div>
        </div>
        {selectedIncident && selectedIncident.video_id === activeVideo?.id ? <IncidentDetails incident={selectedIncident} /> : <div className="flex min-h-[180px] flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/45 p-5 text-center"><ShieldAlert className="mb-2 h-6 w-6 text-slate-600" /><span className="font-mono text-xs text-slate-500">Select an incident for evidence and recommendation.</span></div>}
      </div>
    </PageContainer>
  );
};
