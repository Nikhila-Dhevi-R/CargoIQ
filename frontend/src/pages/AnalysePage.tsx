import React, { useState } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { VideoUploader } from '../components/video/VideoUploader';
import { VideoUrlInput } from '../components/video/VideoUrlInput';
import { AnalysisProgress } from '../components/video/AnalysisProgress';
import { useVideos, useStartAnalysis } from '../api/videos';
import { useAppStore } from '../stores/useAppStore';
import { Video as VideoType } from '../types';
import { Video, UploadCloud, Link2, Sparkles } from 'lucide-react';

export const AnalysePage: React.FC = () => {
  const [tab, setTab] = useState<'upload' | 'url'>('upload');
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);

  const { data: videos, refetch } = useVideos();
  const startAnalysisMutation = useStartAnalysis();
  const { setAnalysisState } = useAppStore();

  const handleIngestSuccess = (data: any) => {
    refetch();
    if (data.job_id) {
      setCurrentJobId(data.job_id);
      setAnalysisState(true, data.job_id, 0, 'Analysis queued');
    }
  };

  const handleTriggerAnalysis = async (videoId: number) => {
    try {
      const res = await startAnalysisMutation.mutateAsync(videoId);
      if (res.job_id) {
        setCurrentJobId(res.job_id);
        setAnalysisState(true, res.job_id, 0, 'Analysis started');
      }
    } catch {
      // Handled
    }
  };

  return (
    <PageContainer
      title="VIDEO INGESTION & PIPELINE ANALYSIS"
      subtitle="Ingest warehouse video streams or surveillance files to run real-time perception, tracking, and SOP evaluation."
    >
      {/* Real-time Analysis Progress Banner (if active job) */}
      {currentJobId && (
        <AnalysisProgress
          jobId={currentJobId}
          onComplete={() => {
            refetch();
          }}
        />
      )}

      {/* Ingestion Methods Card */}
      <div className="rounded-xl glass-panel border border-slate-800 p-6 space-y-6">
        {/* Tab Switcher */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-4">
          <button
            onClick={() => setTab('upload')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
              tab === 'upload'
                ? 'bg-rose-600 text-white shadow-md shadow-rose-950/40'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200'
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload File (MP4/AVI/MOV)</span>
          </button>

          <button
            onClick={() => setTab('url')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
              tab === 'url'
                ? 'bg-rose-600 text-white shadow-md shadow-rose-950/40'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Link2 className="w-4 h-4" />
            <span>Direct Video URL</span>
          </button>
        </div>

        {/* Tab Content */}
        {tab === 'upload' ? (
          <VideoUploader onSuccess={handleIngestSuccess} />
        ) : (
          <VideoUrlInput onSuccess={handleIngestSuccess} />
        )}
      </div>

      {/* Ingested Feeds Library */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider flex items-center gap-2">
          <Video className="w-4 h-4 text-rose-500" />
          Ingested Warehouse Video Feeds ({videos?.length || 0})
        </h3>

        {videos && videos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((v: VideoType) => (
              <div
                key={v.id}
                className="p-4 rounded-xl glass-card border border-slate-800/80 space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-mono text-xs text-rose-400 font-semibold">FEED #{v.id}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase ${
                      v.status === 'completed' ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-700/40' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {v.status}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-100 tracking-tight mt-1 truncate">
                    {v.original_name}
                  </h4>
                  <div className="flex items-center gap-3 text-xs font-mono text-slate-400 mt-2">
                    <span>{v.duration}s</span>
                    <span>•</span>
                    <span>{v.fps} FPS</span>
                    <span>•</span>
                    <span>{v.width}x{v.height}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500">
                    {v.created_at ? new Date(v.created_at).toLocaleDateString() : 'Active'}
                  </span>
                  <button
                    onClick={() => handleTriggerAnalysis(v.id)}
                    disabled={startAnalysisMutation.isPending}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/40 border border-rose-600/40 text-rose-300 text-xs font-mono font-medium transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Run Analysis</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center glass-panel rounded-xl border border-slate-800 text-slate-400 font-mono text-xs">
            No video feeds available. Upload a file or paste a video URL above.
          </div>
        )}
      </div>
    </PageContainer>
  );
};
