import React, { useState } from 'react';
import { Link2, Sparkles, AlertCircle } from 'lucide-react';
import { useUploadVideoUrl } from '../../api/videos';

interface VideoUrlInputProps {
  onSuccess: (data: any) => void;
}

export const VideoUrlInput: React.FC<VideoUrlInputProps> = ({ onSuccess }) => {
  const [url, setUrl] = useState('');
  const [autoAnalyse, setAutoAnalyse] = useState(true);

  const mutation = useUploadVideoUrl();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    try {
      const res = await mutation.mutateAsync({ url: url.trim(), autoAnalyse });
      setUrl('');
      onSuccess(res);
    } catch {
      // Error handled by mutation state
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-xs font-mono uppercase tracking-wider text-slate-400 block mb-2">
          Direct Video Stream or File URL (MP4 / Web Video)
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
            <Link2 className="w-4 h-4" />
          </div>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/cctv/bay1_camera_feed.mp4"
            className="w-full rounded-xl bg-slate-900 border border-slate-800 pl-10 pr-4 py-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-rose-500"
            required
          />
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <label className="flex items-center gap-2 cursor-pointer text-xs font-mono text-slate-300">
          <input
            type="checkbox"
            checked={autoAnalyse}
            onChange={(e) => setAutoAnalyse(e.target.checked)}
            className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-rose-600 focus:ring-rose-500 focus:ring-offset-0"
          />
          <span>Start video analysis immediately upon download</span>
        </label>

        <button
          type="submit"
          disabled={mutation.isPending || !url.trim()}
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md shadow-rose-900/30 transition-all disabled:opacity-50"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{mutation.isPending ? 'Fetching Stream...' : 'Fetch & Analyse URL'}</span>
        </button>
      </div>

      {mutation.isError && (
        <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800/60 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{(mutation.error as any)?.message || 'Failed to download video from URL.'}</span>
        </div>
      )}
    </form>
  );
};
