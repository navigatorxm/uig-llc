"use client";
import { useEffect, useState } from "react";
import { leadsApi, Lead, PipelineStage } from "@/lib/api";

const STAGE_OPTIONS: PipelineStage[] = [
  "new_lead", "contact_initiated", "response_received", "qualified",
  "docs_requested", "docs_received", "under_verification",
  "approved", "visit_scheduled", "closed_won", "closed_lost",
  "cold_lead", "pending_docs",
];

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stage, setStage] = useState<PipelineStage | "">("");
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    setLoading(true);
    leadsApi
      .list(stage ? { stage } : {})
      .then((r) => setLeads(r.data))
      .finally(() => setLoading(false));
  }, [stage]);

  const filteredLeads = leads.filter(
    (l) =>
      l.owner_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (l.phone && l.phone.includes(searchTerm)) ||
      (l.email && l.email.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Leads Management</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {leads.length} total leads · {leads.filter(l => l.response_received).length} responded
            </p>
          </div>
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Search leads..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="border border-gray-200 rounded-lg px-4 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all"
            />
            <select
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/30"
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
        </div>
      </header>

      <div className="p-8">
        {loading ? (
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-14 bg-white rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">ID</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Owner</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Phone</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Email</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Stage</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Score</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Responded</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Interested</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filteredLeads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-blue-50/30 transition-colors">
                    <td className="px-4 py-3 text-gray-400 font-mono text-xs">#{lead.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-800">{lead.owner_name}</td>
                    <td className="px-4 py-3 text-gray-500">{lead.phone || "—"}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{lead.email || "—"}</td>
                    <td className="px-4 py-3">
                      <span className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium">
                        {lead.pipeline_stage.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded ${
                          lead.lead_score >= 70
                            ? "text-green-700 bg-green-50"
                            : lead.lead_score >= 40
                            ? "text-yellow-700 bg-yellow-50"
                            : "text-gray-400 bg-gray-50"
                        }`}
                      >
                        {lead.lead_score.toFixed(0)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {lead.response_received ? (
                        <span className="inline-flex items-center gap-1 text-green-600 text-xs font-medium">
                          <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> Yes
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">No</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {lead.interested === true ? (
                        <span className="text-blue-600 text-xs font-medium">Yes</span>
                      ) : lead.interested === false ? (
                        <span className="text-red-400 text-xs">No</span>
                      ) : (
                        <span className="text-gray-300 text-xs">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredLeads.length === 0 && (
              <p className="text-center py-12 text-gray-400 text-sm">No leads found.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
