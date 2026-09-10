import React, { useState } from 'react';
import { Incident } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { useReviewIncident } from '../../api/incidents';
import { useExplainIncident } from '../../api/assistant';
import { Modal } from '../common/Modal';
import { FeedbackWidget } from '../feedback/FeedbackWidget';
import {
  CheckCircle,
  AlertTriangle,
  Play,
  Bot,
  ShieldCheck,
  XCircle,
  FileText,
  Sparkles,
  Layers,
  MapPin,
  Clock,
  Check,
  Flame,
  MessageSquare
} from 'lucide-react';

interface IncidentDetailsProps {
  incident: Incident;
  onClose?: () => void;
}

export const IncidentDetails: React.FC<IncidentDetailsProps> = ({ incident, onClose }) => {
  const reviewMutation = useReviewIncident();
  const explainMutation = useExplainIncident();

  const [isReplayOpen, setIsReplayOpen] = useState(false);
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);

  const handleReview = (status: 'REVIEWED' | 'DISMISSED') => {
    reviewMutation.mutate({
      id: incident.id,
      status,
      notes: status === 'REVIEWED' ? 'Reviewed and verified by supervisor.' : 'Dismissed as non-critical.'
    });
  };

  const handleExplain = async () => {
    setIsExplainOpen(true);
    if (!aiExplanation) {
      try {
        const res = await explainMutation.mutateAsync(incident.id);
        setAiExplanation(res.full_explanation);
      } catch {
        setAiExplanation('Unable to contact local AI assistant. Please ensure Ollama is active.');
      }
    }
  };

  return (
    <div className="glass-panel rounded-xl border border-slate-800 p-5 space-y-5">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-rose-500 font-semibold uppercase tracking-wider">
              EVENT #{incident.id}
            </span>
            <span className="text-slate-600">•</span>
            <span className="font-mono text-xs text-slate-400">{incident.timestamp}</span>
            <StatusBadge type="review" value={incident.review_status} size="sm" />
          </div>
          <h3 className="text-lg font-bold text-slate-100 mt-1">
            {incident.behaviour_name}
          </h3>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs font-mono text-slate-400">Risk Score</div>
            <div className="text-2xl font-black font-mono text-rose-400 leading-none">
              {incident.risk_score}
              <span className="text-xs text-slate-500 font-normal">/100</span>
            </div>
          </div>
          <StatusBadge type="risk" value={incident.risk_level} size="lg" />
        </div>
      </div>

      {/* Target & Zone Grid */}
      <div className="grid grid-cols-2 gap-3 text-xs font-mono">
        <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
          <span className="text-slate-500 uppercase block mb-1">Tracked Object</span>
          <span className="font-semibold text-rose-300 text-sm">{incident.object_id}</span>
        </div>
        <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
          <span className="text-slate-500 uppercase block mb-1">Operational Zone</span>
          <span className="font-semibold text-slate-200 text-sm">{incident.zone}</span>
        </div>
      </div>

      {/* Algorithmic Evidence Checklist */}
      <div>
        <h4 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-2">
          <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
          Algorithmic Evidence Chain
        </h4>
        <div className="space-y-1.5">
          {incident.evidence.map((ev, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs text-slate-300"
            >
              <Check className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
              <span>{ev}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Deterministic Risk Factor Contribution Breakdown */}
      {incident.factors && incident.factors.length > 0 && (
        <div>
          <h4 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-2">
            <Flame className="w-3.5 h-3.5 text-rose-500" />
            Deterministic Factor Scoring
          </h4>
          <div className="space-y-2 p-3 rounded-xl bg-slate-900/70 border border-slate-800">
            {incident.factors.map((f, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-300">{f.name}</span>
                  <span className="text-rose-400 font-semibold">{f.contribution} pts</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-rose-500 h-full rounded-full"
                    style={{ width: `${Math.min(100, (f.contribution / 35) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SOP Rule & Recommendation */}
      <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-900/40 space-y-2">
        <div className="flex items-center gap-2 text-rose-400 font-mono text-xs font-semibold">
          <FileText className="w-4 h-4" />
          <span>SOP RULE: {incident.sop_rule_code || incident.behaviour}</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          <strong className="text-slate-100">Recommendation: </strong>
          {incident.recommendation}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2">
        <button
          onClick={() => setIsReplayOpen(true)}
          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md shadow-rose-900/30 transition-colors"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Replay Clip</span>
        </button>

        <button
          onClick={handleExplain}
          disabled={explainMutation.isPending}
          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-700 text-cyan-300 font-medium text-xs transition-colors"
        >
          <Bot className="w-3.5 h-3.5 text-cyan-400" />
          <span>{explainMutation.isPending ? 'Consulting AI...' : 'Explain With AI'}</span>
        </button>

        <button
          onClick={() => setIsFeedbackOpen(true)}
          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-700 text-slate-300 font-medium text-xs transition-colors col-span-2 sm:col-span-1"
        >
          <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
          <span>Provide Feedback</span>
        </button>
      </div>

      {/* Review Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-800/80">
        <span className="text-xs font-mono text-slate-500">Review Status:</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleReview('REVIEWED')}
            disabled={reviewMutation.isPending || incident.review_status === 'REVIEWED'}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-700/60 text-emerald-300 text-xs font-medium transition-colors disabled:opacity-50"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Mark Reviewed</span>
          </button>
          <button
            onClick={() => handleReview('DISMISSED')}
            disabled={reviewMutation.isPending || incident.review_status === 'DISMISSED'}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-700 text-slate-400 text-xs font-medium transition-colors disabled:opacity-50"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Dismiss</span>
          </button>
        </div>
      </div>

      {/* Replay Clip Modal */}
      <Modal
        isOpen={isReplayOpen}
        onClose={() => setIsReplayOpen(false)}
        title={`INCIDENT REPLAY - EVENT #${incident.id} (${incident.timestamp})`}
      >
        <div className="space-y-3">
          <div className="aspect-video w-full rounded-lg overflow-hidden bg-black border border-slate-800">
            <video
              src={`/api/events/${incident.id}/replay`}
              controls
              autoPlay
              className="w-full h-full object-contain"
            />
          </div>
          <p className="text-xs font-mono text-slate-400">
            Replay window: 3s before incident to 3s after impact. Evidence stamped on visual frame.
          </p>
        </div>
      </Modal>

      {/* Explain With AI Modal */}
      <Modal
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title={`AI OPERATIONAL BRIEFING - EVENT #${incident.id}`}
        maxWidth="max-w-2xl"
      >
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-900/40 text-slate-200 text-sm leading-relaxed whitespace-pre-line font-sans">
            {explainMutation.isPending ? (
              <div className="flex items-center gap-3 py-4 text-cyan-400">
                <Sparkles className="w-5 h-5 animate-spin" />
                <span>Ollama (qwen2.5:3b) synthesizing grounded explanation...</span>
              </div>
            ) : (
              aiExplanation
            )}
          </div>
          <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-2 flex justify-between">
            <span>Grounded against CargoIQ SOP rules and recorded telemetry</span>
            <span>Evidence-based response</span>
          </div>
        </div>
      </Modal>

      {/* User Feedback Modal */}
      <Modal
        isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
        title={`DETECTION FEEDBACK - EVENT #${incident.id}`}
        maxWidth="max-w-lg"
      >
        <FeedbackWidget
          eventId={incident.id}
          onSuccess={() => setIsFeedbackOpen(false)}
        />
      </Modal>
    </div>
  );
};
