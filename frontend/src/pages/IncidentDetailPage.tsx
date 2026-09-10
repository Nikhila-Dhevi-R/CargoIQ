import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '../components/layout/PageContainer';
import { IncidentDetails } from '../components/incidents/IncidentDetails';
import { useIncident } from '../api/incidents';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ArrowLeft, AlertCircle } from 'lucide-react';

export const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const eventId = id ? parseInt(id, 10) : undefined;

  const { data: incident, isLoading, error } = useIncident(eventId);

  return (
    <PageContainer
      title={incident ? `INCIDENT AUDIT: EVENT #${incident.id}` : 'INCIDENT AUDIT'}
      subtitle="Complete algorithmic evidence breakdown, SOP verification, and replay inspection."
      action={
        <button
          onClick={() => navigate('/incidents')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-mono text-slate-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Incidents</span>
        </button>
      }
    >
      {isLoading ? (
        <LoadingSpinner label="Retrieving incident telemetry..." />
      ) : error || !incident ? (
        <div className="p-8 text-center glass-panel rounded-xl border border-rose-900/40 text-rose-300 font-mono text-xs flex items-center justify-center gap-2">
          <AlertCircle className="w-5 h-5 text-rose-400" />
          <span>Incident record #{id} could not be located.</span>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto">
          <IncidentDetails incident={incident} />
        </div>
      )}
    </PageContainer>
  );
};
