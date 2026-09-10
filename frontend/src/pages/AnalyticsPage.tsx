import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { useAnalyticsOverview } from '../api/analytics';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
  Legend
} from 'recharts';
import { BarChart3, TrendingUp, PieChart as PieIcon, MapPin } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const { data: analytics, isLoading } = useAnalyticsOverview();

  if (isLoading || !analytics) {
    return (
      <PageContainer title="RISK & OPERATIONAL ANALYTICS">
        <LoadingSpinner label="Compiling multi-feed operational analytics..." />
      </PageContainer>
    );
  }

  const { kpis, behaviours, zones, trends } = analytics;

  const riskPieData = [
    { name: 'Critical', value: kpis.critical_events, color: '#e11d48' },
    { name: 'High', value: kpis.high_risk_events, color: '#f43f5e' },
    { name: 'Medium', value: kpis.medium_risk_events, color: '#f59e0b' },
    { name: 'Low', value: kpis.low_risk_events, color: '#0ea5e9' }
  ].filter((d) => d.value > 0);

  return (
    <PageContainer
      title="RISK & OPERATIONAL ANALYTICS"
      subtitle="Data-driven intelligence tracking handling behaviour distributions, zone hotspots, and temporal risk velocity."
    >
      {/* 4 Quick Stat Banners */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Total Movements</span>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-1">{kpis.total_handling_events}</div>
        </div>
        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Anomalies Detected</span>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{kpis.risk_events}</div>
        </div>
        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Preventable Incidents</span>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{kpis.potentially_preventable_incidents}</div>
        </div>
        <div className="p-4 rounded-xl glass-card border border-slate-800">
          <span className="text-xs font-mono text-slate-400 uppercase">Supervisor Verified</span>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">{kpis.reviewed_count}</div>
        </div>
      </div>

      {/* Main Charts Row 1: Behaviour Frequency & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Behaviour Frequency */}
        <div className="lg:col-span-7 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-rose-500" />
              Behaviour Violation Frequency
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Events Count</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={behaviours} layout="vertical" margin={{ left: 40, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis dataKey="behaviour" type="category" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#e11d48" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="lg:col-span-5 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-amber-500" />
              Risk Severity Profile
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Tier Breakdown</span>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {riskPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {riskPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs font-mono text-slate-500">No risk records to display.</p>
            )}
          </div>
        </div>
      </div>

      {/* Main Charts Row 2: Risk Over Time & Zone Risk Hotspots */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Temporal Risk Score Velocity */}
        <div className="lg:col-span-7 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Temporal Risk Trajectory Over Video Timeline
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Score (0-100)</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Line type="monotone" dataKey="score" stroke="#f43f5e" strokeWidth={2.5} dot={{ r: 4, fill: '#f43f5e' }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Zone Hotspots */}
        <div className="lg:col-span-5 p-5 rounded-xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-400" />
              Incidents By Warehouse Zone
            </h3>
            <span className="text-[11px] font-mono text-slate-500">Location Distribution</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={zones} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="zone" stroke="#64748b" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </PageContainer>
  );
};
