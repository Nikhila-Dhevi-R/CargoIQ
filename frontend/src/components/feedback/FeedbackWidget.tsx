import React, { useState } from 'react';
import { useSubmitFeedback } from '../../api/feedback';
import { ThumbsUp, ThumbsDown, HelpCircle, Send, Check } from 'lucide-react';

interface FeedbackWidgetProps {
  eventId: number;
  onSuccess?: () => void;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ eventId, onSuccess }) => {
  const [feedbackType, setFeedbackType] = useState<'correct' | 'incorrect' | 'unsure'>('correct');
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const mutation = useSubmitFeedback();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutation.mutateAsync({
      eventId,
      feedbackType,
      comment: comment.trim() || undefined
    });
    setSubmitted(true);
    if (onSuccess) {
      setTimeout(() => onSuccess(), 1000);
    }
  };

  if (submitted) {
    return (
      <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-700/60 text-center text-emerald-300 font-mono text-xs flex items-center justify-center gap-2">
        <Check className="w-4 h-4" />
        <span>Feedback recorded. Thank you for refining CargoIQ operational accuracy!</span>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-xs font-mono uppercase tracking-wider text-slate-400 block mb-2">
          Was this detection accurate and operationally useful?
        </label>
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            onClick={() => setFeedbackType('correct')}
            className={`flex items-center justify-center gap-2 p-2.5 rounded-lg border text-xs font-medium transition-all ${
              feedbackType === 'correct'
                ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <ThumbsUp className="w-4 h-4 text-emerald-400" />
            <span>Correct</span>
          </button>

          <button
            type="button"
            onClick={() => setFeedbackType('incorrect')}
            className={`flex items-center justify-center gap-2 p-2.5 rounded-lg border text-xs font-medium transition-all ${
              feedbackType === 'incorrect'
                ? 'bg-rose-950/80 border-rose-500 text-rose-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <ThumbsDown className="w-4 h-4 text-rose-400" />
            <span>Incorrect</span>
          </button>

          <button
            type="button"
            onClick={() => setFeedbackType('unsure')}
            className={`flex items-center justify-center gap-2 p-2.5 rounded-lg border text-xs font-medium transition-all ${
              feedbackType === 'unsure'
                ? 'bg-amber-950/80 border-amber-500 text-amber-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <HelpCircle className="w-4 h-4 text-amber-400" />
            <span>Unsure</span>
          </button>
        </div>
      </div>

      <div>
        <label className="text-xs font-mono text-slate-400 block mb-1.5">
          Supervisor Observations (Optional)
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="e.g. Handler pulled carton without trolley; trolley was brought in."
          rows={3}
          className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-rose-500"
        />
      </div>

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md shadow-rose-900/30 transition-colors disabled:opacity-50"
      >
        <Send className="w-3.5 h-3.5" />
        <span>{mutation.isPending ? 'Submitting...' : 'Submit Feedback'}</span>
      </button>
    </form>
  );
};
