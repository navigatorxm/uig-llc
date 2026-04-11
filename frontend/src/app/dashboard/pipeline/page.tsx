"use client";
import { useEffect, useState } from "react";
import { adminPipelineApi, PipelineOverview } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
} from "recharts";

const COLORS = ["#3b82f6", "#06b6d4", "#8b5cf6", "#f59e0b", "#10b981", "#ef4444", "#6366f1", "#ec4899", "#14b8a6", "#f97316", "#64748b", "#a855f7", "#84cc16"];

function formatCrore(amount: number): string {
  if (amount >= 10_000_000) return `₹${(amount / 10_000_000).toFixed(1)} Cr`;
  if (amount >= 100_000) return `₹${(amount / 100_000).toFixed(1)} L`;
  return `₹${amount.toLocaleString("en-IN")}`;
}

function StatCard({ title, value, sub, icon, color }: { title: string; value: string | number; sub?: string; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</p>
          <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className="w-10 h-10 rounded-lg bg-gray-50 flex items-center justify-center text-gray-400">{icon}</div>
      </div>
    </div>
  );
}

export default function PipelineAnalyticsPage() {
  const [data, setData] = useState<PipelineOverview | null>(null);
  const [velocity, setVelocity] = useState<any[]>([]);
  const [funnel, setFunnel] = useState<any[]>([]);
  const [topLeads, setTopLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      adminPipelineApi.overview(),
      adminPipelineApi.leadVelocity(30),
      adminPipelineApi.conversionFunnel(),
      adminPipelineApi.topLeads(15),
    ])
      .then(([overview, vel, fun, top]) => {
        setData(overview.data);
        setVelocity(vel.data.daily_leads || []);
        setFunnel(fun.data.funnel || []);
        setTopLeads(top.data || []);
      })
      .catch((err) => console.error("Pipeline data error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <div key={i} className="h-28 bg-white rounded-xl animate-pulse" />)}
        </div>
        <div className="grid grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => <div key={i} className="h-64 bg-white rounded-xl animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (!data) return <div className="p-8 text-gray-500">Failed to load pipeline data.</div>;

  const stageData = data.pipeline_stages
    ? Object.entries(data.pipeline_stages).map(([stage, count]) => ({
        name: stage.replace(/_/g, " "),
        count,
      }))
    : [];

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <h1 className="text-2xl font-bold text-gray-900">Pipeline Analytics</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Comprehensive pipeline metrics and conversion analysis
        </p>
      </header>

      <div className="p-8 space-y-6">
        {/* Top KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Leads"
            value={data.leads.total.toLocaleString()}
            sub={`${data.leads.today} today · ${data.leads.this_week} this week`}
            color="text-blue-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" /></svg>}
          />
          <StatCard
            title="Response Rate"
            value={`${data.conversion.response_rate}%`}
            sub={`${data.conversion.responded} responded`}
            color="text-green-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
          <StatCard
            title="Win Rate"
            value={`${data.conversion.win_rate}%`}
            sub={`${data.conversion.closed_won} won · ${data.conversion.closed_lost} lost`}
            color="text-purple-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0016.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.27.913c-.721.14-1.472.153-2.202.034M14.25 15.75a4.77 4.77 0 00-2.717-.855c-.974 0-1.9.294-2.718.855" /></svg>}
          />
          <StatCard
            title="Pipeline Value"
            value={formatCrore(data.deals.pipeline_value_inr)}
            sub={`${data.deals.active} active deals`}
            color="text-orange-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
        </div>

        {/* Secondary KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="This Month" value={data.leads.this_month.toLocaleString()} sub="New leads" color="text-cyan-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg>}
          />
          <StatCard title="Outreach Sent" value={data.outreach.total_sent.toLocaleString()} sub={`${data.outreach.sent_this_week} this week`} color="text-indigo-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>}
          />
          <StatCard title="Agent Network" value={data.agents.total} sub={`${data.agents.active_licensed} licensed`} color="text-teal-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" /></svg>}
          />
          <StatCard title="LPI Certificates" value={data.lpi.total_certificates} sub="Issued" color="text-amber-600"
            icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>}
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Lead Velocity */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Lead Velocity (Last 30 Days)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={velocity}>
                <defs>
                  <linearGradient id="velocityGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" fillOpacity={1} fill="url(#velocityGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Stage Distribution */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Pipeline Stage Distribution</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={stageData} barSize={16}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-30} textAnchor="end" height={60} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {stageData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Conversion Funnel */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Conversion Funnel</h3>
          <div className="space-y-2">
            {funnel.map((step: any, i: number) => {
              const maxCount = funnel[0]?.count || 1;
              const width = Math.max((step.count / maxCount) * 100, 4);
              return (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-xs text-gray-500 w-32 text-right capitalize flex-shrink-0">
                    {step.stage.replace(/_/g, " ")}
                  </span>
                  <div className="flex-1 h-7 bg-gray-50 rounded-md relative overflow-hidden">
                    <div
                      className="h-full rounded-md transition-all duration-500"
                      style={{ width: `${width}%`, background: COLORS[i % COLORS.length] }}
                    />
                    <span className="absolute inset-0 flex items-center px-3 text-xs font-semibold text-gray-700">
                      {step.count}
                      {step.drop_off_pct > 0 && (
                        <span className="ml-2 text-red-400 text-[10px]">▼ {step.drop_off_pct}%</span>
                      )}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Leads */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Priority Leads (Top Scored)</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Name</th>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Phone</th>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Stage</th>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Score</th>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Responded</th>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Interested</th>
                  <th className="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Attempts</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {topLeads.map((lead: any) => (
                  <tr key={lead.id} className="hover:bg-blue-50/30 transition-colors">
                    <td className="px-3 py-2.5 font-medium text-gray-800">{lead.owner_name}</td>
                    <td className="px-3 py-2.5 text-gray-500 text-xs">{lead.phone || "—"}</td>
                    <td className="px-3 py-2.5">
                      <span className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">{lead.stage?.replace(/_/g, " ")}</span>
                    </td>
                    <td className="px-3 py-2.5">
                      <span className={`text-xs font-bold ${lead.lead_score >= 70 ? "text-green-600" : lead.lead_score >= 40 ? "text-yellow-600" : "text-gray-400"}`}>
                        {lead.lead_score?.toFixed(0)}
                      </span>
                    </td>
                    <td className="px-3 py-2.5">{lead.response_received ? <span className="text-green-600 text-xs">✓</span> : <span className="text-gray-300">—</span>}</td>
                    <td className="px-3 py-2.5">{lead.interested ? <span className="text-blue-600 text-xs">✓</span> : <span className="text-gray-300">—</span>}</td>
                    <td className="px-3 py-2.5 text-gray-500 text-xs">{lead.contact_attempts || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {topLeads.length === 0 && <p className="text-center py-8 text-gray-400 text-sm">No leads data yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
