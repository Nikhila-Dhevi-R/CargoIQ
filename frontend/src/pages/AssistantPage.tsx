import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { ChatPanel } from '../components/assistant/ChatPanel';
import { Shield, CheckCircle, Cpu } from 'lucide-react';
import { useSystemHealth } from '../api/system';

export const AssistantPage: React.FC = () => {
  const { data: health } = useSystemHealth();

  return (
    <PageContainer
      title="CARGOIQ GROUNDED AI COPILOT"
      subtitle="Operational supervisor conversational assistant backed by FastMCP tools and local Ollama model (qwen2.5:3b)."
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Chat Interface */}
        <div className="lg:col-span-8">
          <ChatPanel />
        </div>

        {/* Right Info & Safety Principles */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-5 rounded-xl glass-panel border border-slate-800 space-y-3">
            <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Intelligence Stack
            </h3>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between p-2 rounded bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400">Local LLM:</span>
                <span className="text-cyan-300 font-semibold">{health?.active_model || 'qwen2.5:3b'}</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400">LLM Status:</span>
                <span className={health?.ollama === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}>
                  {health?.ollama === 'healthy' ? 'CONNECTED' : 'FALLBACK SYNTHESIS'}
                </span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400">Tool Layer:</span>
                <span className="text-slate-200">FastMCP (Read-Only)</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-900/80 border border-slate-800">
                <span className="text-slate-400">Telemetry DB:</span>
                <span className="text-emerald-400">SQLite + SQLAlchemy</span>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-xl glass-panel border border-slate-800 space-y-3">
            <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Shield className="w-4 h-4 text-rose-500" />
              Safety & Verification Rules
            </h3>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <span><strong>No Hallucinations:</strong> The assistant only cites recorded incidents and SOP rules.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <span><strong>Distinguishes Risk vs Damage:</strong> Never asserts physical breakage without empirical evidence.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <span><strong>Privacy Preserving:</strong> Employs anonymous handler tags (e.g. Operator #2).</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <span><strong>Deterministic Scores:</strong> Risk scores are generated mathematically, not by the LLM.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </PageContainer>
  );
};
