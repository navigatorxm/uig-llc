"use client";
import { OverviewStats } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

interface Props {
  stats: OverviewStats;
}

function KpiCard({
  title,
  value,
  sub,
  color,
}: {
  title: string;
  value: string | number;
  sub?: string;
  color: string;
}) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

function formatCrore(amount: number): string {
  if (amount >= 10_000_000) return `₹${(amount / 10_000_000).toFixed(1)} Cr`;
  if (amount >= 100_000) return `₹${(amount / 100_000).toFixed(1)} L`;
  return `₹${amount.toLocaleString("en-IN")}`;
}

export default function MetricsDashboard({ stats }: Props) {
  const ratesData = [
    { name: "Response", value: stats.rates.response_rate_pct },
    { name: "Qualified", value: stats.rates.qualification_rate_pct },
    { name: "Conversion", value: stats.rates.conversion_rate_pct },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard
          title="Total Leads"
          value={stats.leads.total.toLocaleString()}
          sub={`${stats.leads.today} today · ${stats.leads.this_week} this week`}
          color="text-blue-600"
        />
        <KpiCard
          title="Response Rate"
          value={`${stats.rates.response_rate_pct}%`}
          color="text-green-600"
        />
        <KpiCard
          title="Deals Closed"
          value={stats.pipeline.deals_closed_won}
          sub={`${stats.pipeline.active_deals} active`}
          color="text-purple-600"
        />
        <KpiCard
          title="Pipeline Value"
          value={formatCrore(stats.pipeline.pipeline_value_inr)}
          sub={`${stats.pipeline.total_properties_scraped} properties scraped`}
          color="text-orange-600"
        />
      </div>

      {/* Conversion Rates Chart */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Funnel Conversion Rates</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={ratesData} barSize={40}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis unit="%" tick={{ fontSize: 12 }} domain={[0, 100]} />
            <Tooltip formatter={(v) => `${v}%`} />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
