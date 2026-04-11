"use client";
import { useEffect, useState } from "react";
import { leadsApi, Lead, PipelineStage } from "@/lib/api";

const STAGES: Array<{ key: PipelineStage; label: string; color: string }> = [
  { key: "new_lead", label: "New Lead", color: "bg-gray-100 border-gray-300" },
  { key: "contact_initiated", label: "Contact Initiated", color: "bg-blue-50 border-blue-200" },
  { key: "response_received", label: "Response Received", color: "bg-cyan-50 border-cyan-200" },
  { key: "qualified", label: "Qualified", color: "bg-yellow-50 border-yellow-200" },
  { key: "docs_requested", label: "Docs Requested", color: "bg-orange-50 border-orange-200" },
  { key: "docs_received", label: "Docs Received", color: "bg-amber-50 border-amber-200" },
  { key: "under_verification", label: "Under Verification", color: "bg-purple-50 border-purple-200" },
  { key: "approved", label: "Approved", color: "bg-green-50 border-green-200" },
  { key: "visit_scheduled", label: "Visit Scheduled", color: "bg-teal-50 border-teal-200" },
  { key: "closed_won", label: "Closed Won", color: "bg-emerald-50 border-emerald-300" },
  { key: "closed_lost", label: "Closed Lost", color: "bg-red-50 border-red-200" },
  { key: "cold_lead", label: "Cold Lead", color: "bg-slate-100 border-slate-300" },
  { key: "pending_docs", label: "Pending Docs", color: "bg-stone-100 border-stone-300" },
];

function LeadCard({ lead, onStageChange }: { lead: Lead; onStageChange: () => void }) {
  const scoreColor =
    lead.lead_score >= 70
      ? "text-green-600 bg-green-50"
      : lead.lead_score >= 40
        ? "text-yellow-600 bg-yellow-50"
        : "text-gray-500 bg-gray-100";

  return (
    <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100 text-sm space-y-1.5">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-gray-800 leading-tight">{lead.owner_name}</p>
        <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${scoreColor} flex-shrink-0`}>
          {lead.lead_score.toFixed(0)}
        </span>
      </div>
      {lead.phone && (
        <p className="text-xs text-gray-400">{lead.phone}</p>
      )}
      <div className="flex items-center gap-2">
        {lead.response_received && (
          <span className="text-xs text-green-600 bg-green-50 px-1.5 rounded">Replied</span>
        )}
        {lead.interested === true && (
          <span className="text-xs text-blue-600 bg-blue-50 px-1.5 rounded">Interested</span>
        )}
      </div>
    </div>
  );
}

export default function KanbanPipeline() {
  const [leadsByStage, setLeadsByStage] = useState<Record<PipelineStage, Lead[]>>(
    {} as Record<PipelineStage, Lead[]>
  );
  const [loading, setLoading] = useState(true);

  const fetchLeads = async () => {
    setLoading(true);
    const grouped: Record<string, Lead[]> = {};
    STAGES.forEach((s) => (grouped[s.key] = []));

    try {
      const { data } = await leadsApi.list({ limit: 200 });
      data.forEach((lead) => {
        if (grouped[lead.pipeline_stage]) {
          grouped[lead.pipeline_stage].push(lead);
        }
      });
      setLeadsByStage(grouped as Record<PipelineStage, Lead[]>);
    } catch (err) {
      console.error("Failed to load leads", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  if (loading) {
    return (
      <div className="flex gap-3 overflow-x-auto pb-4">
        {STAGES.map((s) => (
          <div
            key={s.key}
            className="flex-shrink-0 w-52 h-64 bg-white rounded-xl animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="flex gap-3 overflow-x-auto pb-4">
      {STAGES.map((stage) => {
        const leads = leadsByStage[stage.key] || [];
        return (
          <div
            key={stage.key}
            className={`flex-shrink-0 w-52 rounded-xl border-2 ${stage.color} p-3`}
          >
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-gray-700 uppercase tracking-wide leading-tight">
                {stage.label}
              </p>
              <span className="text-xs font-bold text-gray-500 bg-white px-1.5 py-0.5 rounded-full border">
                {leads.length}
              </span>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {leads.map((lead) => (
                <LeadCard key={lead.id} lead={lead} onStageChange={fetchLeads} />
              ))}
              {leads.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-4">No leads</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
