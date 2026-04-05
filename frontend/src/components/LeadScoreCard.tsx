"use client";

interface ScoreBreakdown {
  contact_completeness: number;
  listing_freshness: number;
  location_value: number;
  owner_responsiveness: number;
  document_readiness: number;
}

interface Props {
  score: number;
  breakdown: ScoreBreakdown;
  priority: "high" | "medium" | "low";
  reasoning: string;
}

const FACTOR_LABELS: Record<keyof ScoreBreakdown, string> = {
  contact_completeness: "Contact Completeness",
  listing_freshness: "Listing Freshness",
  location_value: "Location Value",
  owner_responsiveness: "Owner Responsiveness",
  document_readiness: "Document Readiness",
};

const MAX_SCORES: Record<keyof ScoreBreakdown, number> = {
  contact_completeness: 25,
  listing_freshness: 20,
  location_value: 20,
  owner_responsiveness: 20,
  document_readiness: 15,
};

const PRIORITY_COLORS = {
  high: "bg-green-100 text-green-800 border-green-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-gray-100 text-gray-600 border-gray-200",
};

export default function LeadScoreCard({ score, breakdown, priority, reasoning }: Props) {
  const ringColor =
    score >= 70 ? "text-green-500" : score >= 40 ? "text-yellow-500" : "text-gray-400";

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 space-y-4">
      {/* Score Circle */}
      <div className="flex items-center gap-4">
        <div className="relative w-20 h-20 flex-shrink-0">
          <svg viewBox="0 0 36 36" className="w-20 h-20 -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3.5" />
            <circle
              cx="18" cy="18" r="15.9"
              fill="none"
              stroke="currentColor"
              strokeWidth="3.5"
              strokeDasharray={`${score} ${100 - score}`}
              className={ringColor}
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-xl font-bold text-gray-800">
            {score.toFixed(0)}
          </span>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800">Lead Score</p>
          <span
            className={`inline-block text-xs font-semibold px-2 py-0.5 rounded border mt-1 uppercase ${PRIORITY_COLORS[priority]}`}
          >
            {priority} priority
          </span>
        </div>
      </div>

      {/* Breakdown */}
      <div className="space-y-2">
        {(Object.keys(breakdown) as (keyof ScoreBreakdown)[]).map((key) => {
          const val = breakdown[key];
          const max = MAX_SCORES[key];
          const pct = (val / max) * 100;
          return (
            <div key={key}>
              <div className="flex justify-between text-xs text-gray-500 mb-0.5">
                <span>{FACTOR_LABELS[key]}</span>
                <span>{val}/{max}</span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Reasoning */}
      {reasoning && (
        <p className="text-xs text-gray-500 italic border-t border-gray-50 pt-3">{reasoning}</p>
      )}
    </div>
  );
}
