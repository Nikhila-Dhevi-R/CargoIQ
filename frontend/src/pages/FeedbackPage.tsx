import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { useFeedbackSummary, useFeedbackList } from '../api/feedback';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { MessageSquare, AlertOctagon } from 'lucide-react';
import { FeedbackItem } from '../types';

export const FeedbackPage: React.FC = () => {
  const { data: summary, isLoading: isSummaryLoading } = useFeedbackSummary();
  const { data: feedbackList, isLoading: isListLoading } = useFeedbackList();

  if (isSummaryLoading || isListLoading) {
    return (
      <PageContainer title="HUMAN-IN-THE-LOOP FEEDBACK AUDIT">
        <LoadingSpinner label="Retrieving supervisor feedback analytics..." />
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title="HUMAN-IN-THE-LOOP FEEDBACK AUDIT"
      subtitle="Operational feedback system allowing supervisors to validate AI detections, record false positives, and tune SOP sensitivity."
    >
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Detection Accuracy</span>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {summary?.accuracy_rate ?? 100}%
          </div>
          <span className="text-[10px] font-mono text-slate-500">Supervisor confirmed</span>
        </div>

        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Total Submissions</span>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
            {summary?.total_feedback ?? 0}
          </div>
          <span className="text-[10px] font-mono text-slate-500">Review responses</span>
        </div>

        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Verified Correct</span>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {summary?.correct_count ?? 0}
          </div>
          <span className="text-[10px] font-mono text-slate-500">True positives</span>
        </div>

        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Disputed / False Positives</span>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">
            {summary?.incorrect_count ?? 0}
          </div>
          <span className="text-[10px] font-mono text-slate-500">Candidate rule adjustments</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Most Disputed Behaviours */}
        <div className="lg:col-span-4 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-rose-500" />
            Most Disputed Rules
          </h3>
          <p className="text-xs text-slate-400">
            Behaviours with reported false alarms used for parameter tuning in <code>godrej_rules.yaml</code>.
          </p>

          <div className="space-y-2">
            {summary?.most_disputed && summary.most_disputed.length > 0 ? (
              summary.most_disputed.map((d: { behaviour: string; count: number }, i: number) => (
                <div key={i} className="flex justify-between items-center p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono">
                  <span className="text-slate-300">{d.behaviour}</span>
                  <span className="text-rose-400 font-semibold">{d.count} disputes</span>
                </div>
              ))
            ) : (
              <div className="p-4 text-center rounded-lg bg-slate-900/40 border border-slate-800 text-xs font-mono text-emerald-400">
                Zero disputed detections recorded.
              </div>
            )}
          </div>
        </div>

        {/* Feedback Feed */}
        <div className="lg:col-span-8 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            Supervisor Feedback Audit Feed ({feedbackList?.length || 0})
          </h3>

          <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
            {feedbackList && feedbackList.length > 0 ? (
              feedbackList.map((fb: FeedbackItem) => (
                <div
                  key={fb.id}
                  className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2"
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-rose-400 font-semibold">EVENT #{fb.event_id}</span>
                      <span className="text-slate-600">•</span>
                      <span className="text-slate-400">{fb.user_id}</span>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase ${
                      fb.feedback_type === 'correct'
                        ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40'
                        : fb.feedback_type === 'incorrect'
                        ? 'bg-rose-950/60 text-rose-400 border border-rose-800/40'
                        : 'bg-amber-950/60 text-amber-400 border border-amber-800/40'
                    }`}>
                      {fb.feedback_type}
                    </span>
                  </div>

                  {fb.comment && (
                    <p className="text-xs text-slate-200 italic font-sans">
                      "{fb.comment}"
                    </p>
                  )}

                  <div className="text-[10px] font-mono text-slate-500 pt-1 border-t border-slate-800/60">
                    Logged: {new Date(fb.created_at).toLocaleString()}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-xs font-mono text-slate-500">
                No feedback submitted yet. Use "Provide Feedback" on any incident card to log human reviews.
              </div>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
};
