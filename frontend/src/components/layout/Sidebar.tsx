import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  AlertTriangle,
  BarChart3,
  BotMessageSquare,
  BookOpenCheck,
  ThumbsUp,
  Settings,
  Flame,
  CheckCircle2
} from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analyse', label: 'Video Analysis', icon: Video },
  { path: '/incidents', label: 'Incidents', icon: AlertTriangle, badge: 'Live' },
  { path: '/analytics', label: 'Risk Analytics', icon: BarChart3 },
  { path: '/assistant', label: 'AI Assistant', icon: BotMessageSquare, highlight: true },
  { path: '/sop', label: 'SOP Rules (10)', icon: BookOpenCheck },
  { path: '/feedback', label: 'User Feedback', icon: ThumbsUp },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const { sidebarOpen } = useAppStore();

  return (
    <aside
      className={`fixed md:sticky top-16 z-30 h-[calc(100vh-4rem)] w-64 border-r border-slate-800/80 bg-slate-950/95 transition-transform duration-300 ease-in-out md:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } flex flex-col justify-between p-4 overflow-y-auto`}
    >
      <div className="space-y-6">
        {/* Section Header */}
        <div className="px-3">
          <p className="text-[11px] font-mono font-semibold uppercase tracking-widest text-slate-400">
            Operations Command
          </p>
        </div>

        {/* Navigation List */}
        <nav className="space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all ${
                    isActive
                      ? 'bg-rose-950/60 text-rose-300 border border-rose-800/40 shadow-sm shadow-rose-950/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-slate-400 group-hover:text-rose-400" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded bg-rose-600/30 text-rose-400 border border-rose-700/40">
                    {item.badge}
                  </span>
                )}
                {item.highlight && (
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer System Disclaimer */}
      <div className="mt-8 p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 text-slate-400">
        <div className="flex items-center gap-2 mb-1.5">
          <Flame className="w-4 h-4 text-rose-500" />
          <span className="text-xs font-semibold text-slate-300 font-mono">DAMAGE PREVENTION</span>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-400">
          Identifies damage-causing behaviour early to prevent losses before packaging failure occurs.
        </p>
      </div>
    </aside>
  );
};
