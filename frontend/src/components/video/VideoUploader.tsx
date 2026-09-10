import React, { useState, useRef } from 'react';
import { UploadCloud, FileVideo, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { useUploadVideo } from '../../api/videos';

interface VideoUploaderProps {
  onSuccess: (data: any) => void;
}

export const VideoUploader: React.FC<VideoUploaderProps> = ({ onSuccess }) => {
  const [dragOver, setDragOver] = useState(false);
  const [autoAnalyse, setAutoAnalyse] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadVideo();

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
        setSelectedFile(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const res = await uploadMutation.mutateAsync({ file: selectedFile, autoAnalyse });
    setSelectedFile(null);
    onSuccess(res);
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`cursor-pointer p-8 rounded-xl border-2 border-dashed transition-all text-center flex flex-col items-center justify-center ${
          dragOver
            ? 'border-rose-500 bg-rose-950/30'
            : selectedFile
            ? 'border-emerald-500/60 bg-emerald-950/20'
            : 'border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/mp4,video/avi,video/quicktime,video/x-matroska"
          onChange={handleFileChange}
          className="hidden"
        />

        {selectedFile ? (
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-600/40 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-100 font-mono">{selectedFile.name}</p>
            <p className="text-xs text-slate-400">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="w-12 h-12 rounded-full bg-slate-800/80 text-rose-500 border border-slate-700 flex items-center justify-center mx-auto">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-200">
              Drop warehouse CCTV video here or <span className="text-rose-400 underline">browse</span>
            </p>
            <p className="text-xs text-slate-500 font-mono">
              Supports MP4, AVI, MOV (Up to 500 MB)
            </p>
          </div>
        )}
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
        <label className="flex items-center gap-2 cursor-pointer text-xs font-mono text-slate-300">
          <input
            type="checkbox"
            checked={autoAnalyse}
            onChange={(e) => setAutoAnalyse(e.target.checked)}
            className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-rose-600 focus:ring-rose-500 focus:ring-offset-0"
          />
          <span>Start video analysis immediately upon upload</span>
        </label>

        {selectedFile && (
          <button
            onClick={handleUpload}
            disabled={uploadMutation.isPending}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md shadow-rose-900/30 transition-all disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{uploadMutation.isPending ? 'Uploading & Processing...' : 'Upload & Ingest'}</span>
          </button>
        )}
      </div>

      {uploadMutation.isError && (
        <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800/60 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{(uploadMutation.error as any)?.message || 'Upload failed.'}</span>
        </div>
      )}
    </div>
  );
};
