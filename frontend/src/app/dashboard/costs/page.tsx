"use client";
import { useEffect, useState } from "react";
import { adminCostsApi, CostOverview } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, LineChart, Line,
} from "recharts";

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#f59e0b", "#10b981", "#ef4444", "#ec4899"];

export default function CostsPage() {
  const [data, setData] = useState<CostOverview | null>(null);
  const [daily, setDaily] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      adminCostsApi.overview(30),
      adminCostsApi.dailyBreakdown(14),
    ])
      .then(([overview, breakdown]) => {
        setData(overview.data);
        setDaily(breakdown.data.daily_spending || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-28 bg-white rounded-xl animate-pulse" />)}
        </div>
        <div className="grid grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => <div key={i} className="h-64 bg-white rounded-xl animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (!data) return <div className="p-8 text-gray-500">Failed to load cost data.</div>;

  const categoryData = Object.entries(data.spending_by_category).map(([name, value]) => ({
    name: name.replace(/_/g, " "),
    value,
  }));

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <h1 className="text-2xl font-bold text-gray-900">Costs & AI Usage</h1>
        <p className="text-sm text-gray-500 mt-0.5">Monitor spending, AI token usage, and wallet balance</p>
      </header>

      <div className="p-8 space-y-6">
        {/* Wallet KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-6 text-white shadow-lg">
            <p className="text-blue-200 text-xs font-medium uppercase tracking-wide">Wallet Balance</p>
            <p className="text-3xl font-bold mt-1">${data.wallet.balance_usd.toFixed(2)}</p>
            <p className="text-blue-200 text-xs mt-2">Available credits</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Credits</p>
            <p className="text-2xl font-bold text-green-600 mt-1">${data.wallet.total_credits.toFixed(2)}</p>
            <p className="text-xs text-gray-400 mt-2">All-time top-ups</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Spending</p>
            <p className="text-2xl font-bold text-red-500 mt-1">${data.wallet.total_debits.toFixed(2)}</p>
            <p className="text-xs text-gray-400 mt-2">All-time expenses</p>
          </div>
        </div>

        {/* AI Usage KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">AI Cost (30d)</p>
            <p className="text-2xl font-bold text-purple-600 mt-1">${data.ai_usage.total_cost_usd.toFixed(4)}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Tokens In (30d)</p>
            <p className="text-2xl font-bold text-cyan-600 mt-1">{data.ai_usage.total_tokens_in.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Tokens Out (30d)</p>
            <p className="text-2xl font-bold text-indigo-600 mt-1">{data.ai_usage.total_tokens_out.toLocaleString()}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Spending by Category */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Spending by Category</h3>
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {categoryData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => `$${v.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-52 flex items-center justify-center text-gray-400 text-sm">No spending data yet</div>
            )}
          </div>

          {/* Daily Spending */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Daily Spending (Last 14 Days)</h3>
            {daily.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={daily} barSize={20}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
                  <Tooltip formatter={(v: number) => `$${v.toFixed(2)}`} />
                  <Bar dataKey="amount_usd" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-52 flex items-center justify-center text-gray-400 text-sm">No daily data yet</div>
            )}
          </div>
        </div>

        {/* AI Usage by Model */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">AI Usage by Model</h3>
          {data.ai_usage.by_model.length > 0 ? (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Model</th>
                  <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Requests</th>
                  <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Tokens In</th>
                  <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Tokens Out</th>
                  <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.ai_usage.by_model.map((m, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-2.5 font-medium text-gray-800">{m.model}</td>
                    <td className="px-4 py-2.5 text-right text-gray-500">{m.requests.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-right text-gray-500">{m.tokens_in.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-right text-gray-500">{m.tokens_out.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-right font-medium text-gray-800">${m.cost_usd.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-center py-8 text-gray-400 text-sm">No AI usage recorded yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
