import { create } from 'zustand';
import { Video, Incident, RiskLevel, ReviewStatus } from '../types';

interface FilterState {
  riskLevel: string;
  behaviour: string;
  zone: string;
  reviewStatus: string;
}

interface AppState {
  selectedVideo: Video | null;
  selectedIncident: Incident | null;
  currentPlaybackTime: number;
  sidebarOpen: boolean;
  activeFilters: FilterState;
  activeJobId: string | null;
  isAnalyzing: boolean;
  analysisProgress: number;
  analysisStatusText: string;

  setSelectedVideo: (video: Video | null) => void;
  setSelectedIncident: (incident: Incident | null) => void;
  setCurrentPlaybackTime: (time: number) => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setFilter: (key: keyof FilterState, value: string) => void;
  resetFilters: () => void;
  setAnalysisState: (isAnalyzing: boolean, jobId: string | null, progress: number, text: string) => void;
  updateAnalysisProgress: (progress: number, text: string) => void;
}

const initialFilters: FilterState = {
  riskLevel: 'ALL',
  behaviour: 'ALL',
  zone: 'ALL',
  reviewStatus: 'ALL'
};

export const useAppStore = create<AppState>((set) => ({
  selectedVideo: null,
  selectedIncident: null,
  currentPlaybackTime: 0,
  sidebarOpen: true,
  activeFilters: initialFilters,
  activeJobId: null,
  isAnalyzing: false,
  analysisProgress: 0,
  analysisStatusText: '',

  setSelectedVideo: (video) => set({ selectedVideo: video }),
  setSelectedIncident: (incident) => set({ selectedIncident: incident }),
  setCurrentPlaybackTime: (time) => set({ currentPlaybackTime: time }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setFilter: (key, value) =>
    set((state) => ({
      activeFilters: { ...state.activeFilters, [key]: value }
    })),
  resetFilters: () => set({ activeFilters: initialFilters }),
  setAnalysisState: (isAnalyzing, jobId, progress, text) =>
    set({
      isAnalyzing,
      activeJobId: jobId,
      analysisProgress: progress,
      analysisStatusText: text
    }),
  updateAnalysisProgress: (progress, text) =>
    set({ analysisProgress: progress, analysisStatusText: text })
}));
