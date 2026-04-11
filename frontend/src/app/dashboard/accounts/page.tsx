"use client";
import { useEffect, useState } from "react";
import { adminAccountsApi, AccountsSummary } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";

function formatINR(amount: number): string {
  if (amount >= 10_000_000) return `₹${(amount / 10_000_000).toFixed(1)} Cr`;
  if (amount >= 100_000) return `₹${(amount / 100_000).toFixed(1)} L`;
  return `₹${amount.toLocaleString("en-IN")}`;
}

export default function AccountsPage() {
  const [summary, setSummary] = useState<AccountsSummary | null>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      adminAccountsApi.summary(),
      adminAccountsApi.monthlyTrend(6),
      adminAccountsApi.transactions({ limit: 20 }),
    ])
      .then(([sum, tr, txs]) => {
        setSummary(sum.data);
        setTrend(tr.data.monthly || []);
        setTransactions(txs.data || []);
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
      </div>
    );
  }

  if (!summary) return <div className="p-8 text-gray-500">Failed to load account data.</div>;

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <h1 className="text-2xl font-bold text-gray-900">Financial Accounts</h1>
        <p className="text-sm text-gray-500 mt-0.5">Financial overview, income, expenses, and category breakdown</p>
      </header>

      <div className="p-8 space-y-6">
        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl p-6 text-white shadow-lg">
            <p className="text-emerald-200 text-xs font-medium uppercase tracking-wide">Net Balance</p>
            <p className="text-3xl font-bold mt-1">{formatINR(summary.balance)}</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Income</p>
            <p className="text-2xl font-bold text-green-600 mt-1">{formatINR(summary.total_credits)}</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Expenses</p>
            <p className="text-2xl font-bold text-red-500 mt-1">{formatINR(summary.total_debits)}</p>
          </div>
        </div>

        {/* This Month */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">This Month Credits</p>
            <p className="text-xl font-bold text-green-600 mt-1">{formatINR(summary.this_month.credits)}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">This Month Debits</p>
            <p className="text-xl font-bold text-red-500 mt-1">{formatINR(summary.this_month.debits)}</p>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">This Month Net</p>
            <p className={`text-xl font-bold mt-1 ${summary.this_month.net >= 0 ? "text-green-600" : "text-red-500"}`}>
              {formatINR(summary.this_month.net)}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Monthly Trend Chart */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Trend (6 Months)</h3>
            {trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatINR(v)} />
                  <Tooltip formatter={(v: number) => formatINR(v)} />
                  <Legend />
                  <Bar dataKey="credits" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="debits" name="Expenses" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-56 flex items-center justify-center text-gray-400 text-sm">No trend data yet</div>
            )}
          </div>

          {/* Category Breakdown */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Category Breakdown</h3>
            <div className="space-y-3">
              {Object.entries(summary.by_category).map(([cat, data]) => (
                <div key={cat} className="flex items-center gap-3">
                  <span className="text-xs text-gray-500 w-28 capitalize flex-shrink-0">{cat.replace(/_/g, " ")}</span>
                  <div className="flex-1 flex items-center gap-3">
                    <span className="text-xs text-green-600 font-medium w-20 text-right">+{formatINR(data.credits)}</span>
                    <span className="text-xs text-red-500 font-medium w-20 text-right">-{formatINR(data.debits)}</span>
                    <span className="text-[10px] text-gray-400">{data.transactions} txns</span>
                  </div>
                </div>
              ))}
              {Object.keys(summary.by_category).length === 0 && (
                <p className="text-sm text-gray-400 text-center py-4">No category data yet.</p>
              )}
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Recent Transactions</h3>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Type</th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Amount</th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Category</th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Description</th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {transactions.map((tx: any) => (
                <tr key={tx.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-2.5">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${tx.transaction_type === "credit" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
                      {tx.transaction_type}
                    </span>
                  </td>
                  <td className={`px-4 py-2.5 font-medium ${tx.transaction_type === "credit" ? "text-green-600" : "text-red-500"}`}>
                    {tx.transaction_type === "credit" ? "+" : "-"}{tx.currency === "INR" ? "₹" : "$"}{tx.amount.toFixed(2)}
                  </td>
                  <td className="px-4 py-2.5 text-gray-500 text-xs capitalize">{tx.category?.replace(/_/g, " ")}</td>
                  <td className="px-4 py-2.5 text-gray-500 text-xs max-w-xs truncate">{tx.description || "—"}</td>
                  <td className="px-4 py-2.5 text-gray-400 text-xs">{new Date(tx.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {transactions.length === 0 && <p className="text-center py-8 text-gray-400 text-sm">No transactions recorded yet.</p>}
        </div>
      </div>
    </div>
  );
}
