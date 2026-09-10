import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, Activity, Cpu, Server, Menu, Radio, Sparkles } from 'lucide-react';
import { useSystemHealth } from '../../api/system';
import { useAppStore } from '../../stores/useAppStore';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { data: health } = useSystemHealth();
  const { toggleSidebar } = useAppStore();

  const isBackendUp = health?.backend === 'healthy';
  const isOllamaUp = health?.ollama === 'healthy';
  const isVisionAvailable = health?.vision_model === 'available';

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        {/* Left: Mobile Toggle & Brand */}
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-850"
            aria-label="Toggle Navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-rose-600 to-rose-900 border border-rose-500/40 shadow-lg shadow-rose-950/50">
              <Shield className="w-5 h-5 text-white group-hover:scale-105 transition-transform" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500" />
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-lg font-bold tracking-wider text-slate-100">CARG<span className="text-rose-500 ml-0.5">OIQ</span></span>
                <span className="px-2 py-0.5 text-[10px] font-mono uppercase rounded bg-rose-950/80 text-rose-300 border border-rose-800/60 font-semibold tracking-wider">
                  Industrial
                </span>
              </div>
              <p className="text-[11px] text-slate-400 tracking-tight hidden sm:block">
                See the Risk. Stop the Damage.
              </p>
            </div>
          </Link>
        </div>

        {/* Right: Live Telemetry & Status Badges */}
        <div className="flex items-center gap-2 sm:gap-3 font-mono text-xs">
          {/* Backend Status */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <Server className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400 text-[11px]">API:</span>
            <span className={`inline-flex items-center gap-1 ${isBackendUp ? 'text-emerald-400' : 'text-rose-400'}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isBackendUp ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
              {isBackendUp ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>

          {/* Ollama Local LLM Status */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400 text-[11px]">OLLAMA:</span>
            <span className={`inline-flex items-center gap-1 ${isOllamaUp ? 'text-emerald-400' : 'text-amber-400'}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isOllamaUp ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              {isOllamaUp ? 'ONLINE (3B)' : 'FALLBACK'}
            </span>
          </div>

          {/* CV Pipeline Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <Activity className="w-3.5 h-3.5 text-rose-500" />
            <span className="text-slate-300 font-semibold text-[11px] hidden sm:inline">VISION:</span>
            <span className={`font-medium text-[11px] ${isVisionAvailable ? 'text-emerald-400' : 'text-amber-400'}`}>{isVisionAvailable ? 'AVAILABLE' : 'UNAVAILABLE'}</span>
          </div>

          {/* Quick Action: New Analysis */}
          <Link
            to="/analyse"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md shadow-rose-900/30 transition-all ml-2"
          >
            <Radio className="w-3.5 h-3.5" />
            <span>Analyse</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
