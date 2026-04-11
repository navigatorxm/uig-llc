import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

let authToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem("auth_token", token);
  } else {
    localStorage.removeItem("auth_token");
  }
};

export const initAuth = () => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    authToken = token;
  }
};

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      setAuthToken(null);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// --- Types ---
export type PipelineStage =
  | "new_lead"
  | "contact_initiated"
  | "response_received"
  | "qualified"
  | "docs_requested"
  | "docs_received"
  | "under_verification"
  | "approved"
  | "visit_scheduled"
  | "closed_won"
  | "closed_lost"
  | "cold_lead"
  | "pending_docs";

export interface Lead {
  id: number;
  owner_name: string;
  phone?: string;
  email?: string;
  whatsapp?: string;
  pipeline_stage: PipelineStage;
  lead_score: number;
  contact_attempt_count: number;
  response_received: boolean;
  interested?: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Property {
  id: number;
  source_portal: string;
  title?: string;
  transaction_type: "buy" | "rent";
  price?: number;
  locality?: string;
  city: string;
  owner_name?: string;
  owner_phone?: string;
  scraped_at: string;
  budget_range?: string;
  location_tag?: string;
}

export interface OverviewStats {
  leads: { total: number; today: number; this_week: number };
  rates: {
    response_rate_pct: number;
    qualification_rate_pct: number;
    conversion_rate_pct: number;
  };
  pipeline: {
    total_properties_scraped: number;
    active_deals: number;
    deals_closed_won: number;
    pipeline_value_inr: number;
  };
}

export interface FunnelData {
  funnel: Array<{ stage: string; count: number }>;
}

// --- API functions ---
export const leadsApi = {
  list: (params?: { stage?: PipelineStage; skip?: number; limit?: number }) =>
    api.get<Lead[]>("/leads", { params }),
  get: (id: number) => api.get<Lead>(`/leads/${id}`),
  updateStage: (id: number, stage: PipelineStage) =>
    api.patch<Lead>(`/leads/${id}/stage`, { stage }),
  getScore: (id: number) => api.get(`/leads/${id}/score`),
};

export const propertiesApi = {
  list: (params?: object) => api.get<Property[]>("/properties", { params }),
  triggerScrape: (data: {
    portal: string;
    location: string;
    transaction_type: string;
    max_pages: number;
  }) => api.post("/scraping/trigger", data),
};

export const analyticsApi = {
  overview: () => api.get<OverviewStats>("/analytics/overview"),
  funnel: () => api.get<FunnelData>("/analytics/funnel"),
  outreach: () => api.get("/analytics/outreach"),
};

export const outreachApi = {
  send: (data: { lead_id: number; channel: "whatsapp" | "email"; template: string }) =>
    api.post("/outreach/send", data),
};
