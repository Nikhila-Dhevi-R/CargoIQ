import React, { useState } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { useIncidents, useReviewIncident } from '../api/incidents';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import { IncidentDetails } from '../components/incidents/IncidentDetails';
import { Incident } from '../types';
import {
  Filter,
  CheckCircle2,
  XCircle,
  Eye,
  RotateCcw
} from 'lucide-react';

export const IncidentsPage: React.FC = () => {
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [reviewFilter, setReviewFilter] = useState('ALL');
  const [zoneFilter, setZoneFilter] = useState('ALL');
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  const { data: incidents } = useIncidents({
    riskLevel: riskFilter,
    reviewStatus: reviewFilter,
    zone: zoneFilter
  });

  const reviewMutation = useReviewIncident();

  const handleQuickReview = (id: number, status: 'REVIEWED' | 'DISMISSED') => {
    reviewMutation.mutate({ id, status });
  };

  return (
    <PageContainer
      title="INCIDENT MANAGEMENT & AUDITING"
      subtitle="Comprehensive audit trail of detected handling anomalies, risk evaluations, and supervisor reviews."
    >
      {/* Filter Toolbar */}
      <div className="p-4 rounded-xl glass-panel border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Filter className="w-3.5 h-3.5 text-rose-500" />
            <span>FILTERS:</span>
          </div>

          {/* Risk Level Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Review Status Filter */}
          <select
            value={reviewFilter}
            onChange={(e) => setReviewFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Review Statuses</option>
            <option value="UNREVIEWED">Unreviewed</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="DISMISSED">Dismissed</option>
          </select>

          {/* Zone Filter */}
          <select
            value={zoneFilter}
            onChange={(e) => setZoneFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Zones</option>
            <option value="Loading Bay 1">Loading Bay 1</option>
            <option value="Loading Bay 2">Loading Bay 2</option>
            <option value="Staging Zone A">Staging Zone A</option>
            <option value="Staging Zone B">Staging Zone B</option>
            <option value="General Walkway">General Walkway</option>
            <option value="Dispatch Area">Dispatch Area</option>
          </select>
        </div>

        <button
          onClick={() => {
            setRiskFilter('ALL');
            setReviewFilter('ALL');
            setZoneFilter('ALL');
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Incidents Table / Card Grid */}
      <div className="space-y-3">
        {incidents && incidents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {incidents.map((inc: Incident) => (
              <div
                key={inc.id}
                className="p-5 rounded-xl glass-card border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-rose-500 font-semibold">EVENT #{inc.id}</span>
                      <span className="text-slate-600">•</span>
                      <span className="font-mono text-xs text-slate-400">{inc.timestamp}</span>
                    </div>
                    <StatusBadge type="risk" value={inc.risk_level} size="sm" />
                  </div>

                  <h4 className="text-base font-bold text-slate-100 mt-2 tracking-tight">
                    {inc.behaviour_name}
                  </h4>

                  <div className="mt-2 space-y-1 text-xs font-mono text-slate-400">
                    <div>Target: <span className="text-rose-300 font-semibold">{inc.object_id}</span></div>
                    <div>Location: <span className="text-slate-300">{inc.zone}</span></div>
                    <div>Algorithmic Risk: <span className="text-rose-400 font-bold">{inc.risk_score}/100</span></div>
                  </div>

                  {/* Primary Evidence summary */}
                  <div className="mt-3 p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 line-clamp-2">
                    {inc.evidence[0] || 'Handling anomaly observed on frame buffer.'}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <button
                    onClick={() => setSelectedIncident(inc)}
                    className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300 font-medium"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Inspect Evidence</span>
                  </button>

                  <div className="flex items-center gap-1.5">
                    {inc.review_status === 'UNREVIEWED' ? (
                      <>
                        <button
                          onClick={() => handleQuickReview(inc.id, 'REVIEWED')}
                          className="p-1.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-400 border border-emerald-800/40"
                          title="Mark Reviewed"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleQuickReview(inc.id, 'DISMISSED')}
                          className="p-1.5 rounded-lg bg-slate-850 hover:bg-slate-800 text-slate-400 border border-slate-700"
                          title="Dismiss"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </>
                    ) : (
                      <StatusBadge type="review" value={inc.review_status} size="sm" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center glass-panel rounded-xl border border-slate-800 text-slate-400 font-mono text-xs">
            No incidents matched the selected filter criteria.
          </div>
        )}
      </div>

      {/* Incident Detail Modal */}
      {selectedIncident && (
        <Modal
          isOpen={Boolean(selectedIncident)}
          onClose={() => setSelectedIncident(null)}
          title={`INCIDENT INSPECTOR - EVENT #${selectedIncident.id}`}
          maxWidth="max-w-3xl"
        >
          <IncidentDetails incident={selectedIncident} />
        </Modal>
      )}
    </PageContainer>
  );
};
