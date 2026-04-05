"use client";
import { useEffect, useState } from "react";
import { leadsApi, Lead, PipelineStage } from "@/lib/api";

const STAGE_OPTIONS: PipelineStage[] = [
  "new_lead", "contact_initiated", "response_received", "qualified",
  "docs_requested", "docs_received", "under_verification",
  "approved", "visit_scheduled", "closed_won", "closed_lost",
];

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stage, setStage] = useState<PipelineStage | "">("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    leadsApi
      .list(stage ? { stage } : {})
      .then((r) => setLeads(r.data))
      .finally(() => setLoading(false));
  }, [stage]);

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
        <select
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
          value={stage}
          onChange={(e) => setStage(e.target.value as PipelineStage | "")}
        >
          <option value="">All Stages</option>
          {STAGE_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading leads...</div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Owner</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Phone</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Stage</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Score</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Responded</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-400">#{lead.id}</td>
                  <td className="px-4 py-3 font-medium text-gray-800">{lead.owner_name}</td>
                  <td className="px-4 py-3 text-gray-500">{lead.phone || "—"}</td>
                  <td className="px-4 py-3">
                    <span className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                      {lead.pipeline_stage.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`text-xs font-bold ${
                        lead.lead_score >= 70
                          ? "text-green-600"
                          : lead.lead_score >= 40
                          ? "text-yellow-600"
                          : "text-gray-400"
                      }`}
                    >
                      {lead.lead_score.toFixed(0)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {lead.response_received ? (
                      <span className="text-green-600 text-xs">Yes</span>
                    ) : (
                      <span className="text-gray-400 text-xs">No</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {leads.length === 0 && (
            <p className="text-center py-8 text-gray-400 text-sm">No leads found.</p>
          )}
        </div>
      )}
    </div>
  );
}
