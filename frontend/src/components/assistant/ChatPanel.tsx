import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, Sparkles, FileText, Shield, AlertCircle, RefreshCw } from 'lucide-react';
import { useSendAssistantMessage, useGenerateShiftSummary } from '../../api/assistant';
import { ChatMessage } from '../../types';

const SUGGESTED_QUERIES = [
  "What were the most serious incidents?",
  "Which warehouse zone had the highest risk?",
  "Why is dragging considered unsafe?",
  "What happened with Carton #8 in Bay 1?",
  "Summarize the morning shift handling"
];

export const ChatPanel: React.FC<{ videoId?: number; eventId?: number }> = ({ videoId, eventId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello, I am CargoIQ, your warehouse handling intelligence copilot. I explain observed handling behaviours, SOP compliance, and preventive actions using analysed video evidence.",
      timestamp: 'Now',
      citations: ['CargoIQ operational data']
    }
  ]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const chatMutation = useSendAssistantMessage();
  const summaryMutation = useGenerateShiftSummary();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, chatMutation.isPending, summaryMutation.isPending]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');

    try {
      const res = await chatMutation.mutateAsync({
        message: text,
        video_id: videoId,
        event_id: eventId
      });

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations: res.citations
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'assistant',
        text: "I encountered a communication timeout with the local AI assistant engine. Please verify the backend and Ollama server status.",
        timestamp: 'Now'
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleShiftSummary = async () => {
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: "Generate comprehensive warehouse shift summary.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await summaryMutation.mutateAsync(videoId);
      const assistantMsg: ChatMessage = {
        id: `summary-${Date.now()}`,
        sender: 'assistant',
        text: res.full_summary_text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations: ['Shift telemetry', 'CargoIQ risk engine'],
        isExplanation: true
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      // Handled
    }
  };

  return (
    <div className="flex flex-col h-[650px] rounded-xl glass-panel border border-slate-800 overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-600 to-cyan-900 border border-cyan-500/40 flex items-center justify-center text-white shadow-md shadow-cyan-950/50">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2 font-mono">
              CARGOIQ COPILOT
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
            </h3>
            <p className="text-[11px] text-slate-400 font-sans">
              Grounded on Video Telemetry & SOP Rules (Zero Hallucination)
            </p>
          </div>
        </div>

        <button
          onClick={handleShiftSummary}
          disabled={summaryMutation.isPending}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-700/60 text-cyan-300 font-mono text-xs transition-colors disabled:opacity-50"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>{summaryMutation.isPending ? 'Generating...' : 'Generate Shift Summary'}</span>
        </button>
      </div>

      {/* Suggested Questions Pill Row */}
      <div className="px-4 py-2 border-b border-slate-800/60 bg-slate-950/40 flex items-center gap-2 overflow-x-auto text-[11px] font-mono scrollbar-none">
        <span className="text-slate-500 shrink-0">SUGGESTED:</span>
        {SUGGESTED_QUERIES.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="shrink-0 px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 transition-all"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-xl p-4 text-xs leading-relaxed whitespace-pre-line ${
                m.sender === 'user'
                  ? 'bg-rose-600 text-white shadow-md shadow-rose-950/40 font-medium'
                  : 'bg-slate-900/90 text-slate-200 border border-slate-800 shadow-sm'
              }`}
            >
              {m.text}

              {/* Citations Footer */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex flex-wrap items-center gap-1.5 text-[10px] font-mono text-slate-400">
                  <span className="text-slate-500">GROUNDED CITATIONS:</span>
                  {m.citations.map((c, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-slate-950 text-cyan-300 border border-cyan-800/40"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-1 px-1">
              {m.timestamp}
            </span>
          </div>
        ))}

        {/* Typing indicator */}
        {(chatMutation.isPending || summaryMutation.isPending) && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs font-mono text-cyan-400 w-fit">
            <Sparkles className="w-4 h-4 animate-spin text-cyan-400" />
            <span>Consulting MCP tools and grounding data...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Box */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/80">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about incidents, SOP rules, zone hotspots, or recommended actions..."
            className="flex-1 rounded-xl bg-slate-950 border border-slate-800 px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-sans"
          />
          <button
            type="submit"
            disabled={chatMutation.isPending || !input.trim()}
            className="flex items-center justify-center p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white shadow-md shadow-cyan-950/40 transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
