export type RiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ReviewStatus = 'UNREVIEWED' | 'REVIEWED' | 'DISMISSED';

export interface FactorBreakdown {
  name: string;
  contribution: number;
  description?: string;
}

export interface TrackedObjectSnapshot {
  track_id: number;
  class_name: string;
  label: string;
  confidence: number;
  /** Normalized [x1, y1, x2, y2] box from the backend detector. */
  bbox: [number, number, number, number];
}

export interface IncidentMetadata {
  subject?: TrackedObjectSnapshot;
  worker?: TrackedObjectSnapshot | null;
  related_objects?: TrackedObjectSnapshot[];
  tracks?: TrackedObjectSnapshot[];
}

export interface FrameObservation {
  frame: number;
  timestamp_seconds: number;
  tracks: TrackedObjectSnapshot[];
}

export interface Incident {
  id: number;
  video_id: number;
  timestamp: string;
  timestamp_seconds: number;
  behaviour: string;
  behaviour_name: string;
  object_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  zone: string;
  evidence: string[];
  recommendation: string;
  clip_path?: string | null;
  review_status: ReviewStatus;
  review_notes?: string | null;
  confidence: number;
  severity: string;
  duration: number;
  factors: FactorBreakdown[];
  sop_rule_code?: string;
  created_at?: string;
  display_label?: string;
  metadata?: IncidentMetadata;
}

export interface Video {
  id: number;
  filename: string;
  original_name: string;
  duration: number;
  fps: number;
  width: number;
  height: number;
  status: 'ready' | 'processing' | 'completed' | 'failed';
  file_path: string;
  processed_path?: string | null;
  thumbnail_path?: string | null;
  created_at?: string;
}

export interface AnalysisJob {
  job_id: string;
  video_id: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_frame: number;
  total_frames: number;
  step_description: string;
  error_message?: string | null;
}

export interface OverviewKPIs {
  total_videos_analysed: number;
  total_handling_events: number;
  risk_events: number;
  critical_events: number;
  high_risk_events: number;
  medium_risk_events: number;
  low_risk_events: number;
  potentially_preventable_incidents: number;
  reviewed_count: number;
}

export interface BehaviourStat {
  behaviour: string;
  count: number;
  avg_risk: number;
}

export interface ZoneStat {
  zone: string;
  count: number;
  avg_risk: number;
}

export interface TrendItem {
  time: string;
  score: number;
  level: RiskLevel;
  behaviour: string;
}

export interface AnalyticsOverview {
  kpis: OverviewKPIs;
  behaviours: BehaviourStat[];
  zones: ZoneStat[];
  trends: TrendItem[];
}

export interface SopRule {
  code: string;
  name: string;
  severity: string;
  description: string;
  conditions: Record<string, any>;
  evidence_templates?: string[];
  recommendation: string;
}

export interface FeedbackSummary {
  total_feedback: number;
  correct_count: number;
  incorrect_count: number;
  unsure_count: number;
  accuracy_rate: number;
  most_disputed: Array<{ behaviour: string; count: number }>;
}

export interface FeedbackItem {
  id: number;
  event_id: number;
  feedback_type: 'correct' | 'incorrect' | 'unsure';
  comment?: string;
  user_id: string;
  created_at: string;
}

export interface SystemHealth {
  backend: string;
  database: string;
  ollama: string;
  vision_model: string;
  ffmpeg: string;
  active_model?: string;
  yolo_model?: string;
  confidence_threshold?: number;
  clip_pre_seconds?: number;
  clip_post_seconds?: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  citations?: string[];
  isExplanation?: boolean;
}
