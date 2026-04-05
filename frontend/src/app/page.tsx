"use client";
import { useEffect, useState } from "react";
import { analyticsApi, OverviewStats } from "@/lib/api";
import MetricsDashboard from "@/components/MetricsDashboard";
import KanbanPipeline from "@/components/KanbanPipeline";

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.overview().then((r) => {
      setStats(r.data);
      setLoading(false);
    });
  }, []);

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            UIG Property Acquisition Pipeline
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            United Investing Group LLC · Delhi NCR Operations
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-700">Philip George</p>
          <p className="text-xs text-gray-400">Property Acquisition Manager · Head of Asia Pacific</p>
        </div>
      </header>

      <div className="px-8 py-6 space-y-8">
        {/* KPI Cards */}
        {loading ? (
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-28 bg-white rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          stats && <MetricsDashboard stats={stats} />
        )}

        {/* Pipeline Kanban */}
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Lead Pipeline</h2>
          <KanbanPipeline />
        </div>
      </div>
    </main>
  );
}
