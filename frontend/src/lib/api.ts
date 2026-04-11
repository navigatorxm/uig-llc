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

export const getAuthToken = () => authToken || localStorage.getItem("auth_token");

api.interceptors.request.use((config) => {
  const token = authToken || localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      setAuthToken(null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
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

export type UserRole = "master_admin" | "admin" | "sub_agent";

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

export interface AdminUser {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  last_login_at?: string;
  login_count: number;
  created_at: string;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  full_name: string;
}

export interface PipelineOverview {
  leads: { total: number; today: number; this_week: number; this_month: number };
  pipeline_stages: Record<string, number>;
  conversion: {
    response_rate: number;
    interest_rate: number;
    win_rate: number;
    responded: number;
    interested: number;
    closed_won: number;
    closed_lost: number;
  };
  outreach: { total_sent: number; sent_this_week: number };
  properties: { total_scraped: number };
  deals: { active: number; pipeline_value_inr: number };
  agents: { total: number; active_licensed: number };
  lpi: { total_certificates: number };
}

export interface CostOverview {
  wallet: { balance_usd: number; total_credits: number; total_debits: number };
  spending_by_category: Record<string, number>;
  ai_usage: {
    total_cost_usd: number;
    total_tokens_in: number;
    total_tokens_out: number;
    by_model: Array<{ model: string; requests: number; tokens_in: number; tokens_out: number; cost_usd: number }>;
  };
  period_days: number;
}

export interface SystemSettingItem {
  id: number;
  key: string;
  value: string;
  category: string;
  is_secret: boolean;
  description?: string;
  updated_at: string;
  updated_by?: string;
}

export interface AutomationWorkflow {
  id: number;
  name: string;
  description?: string;
  natural_language_prompt: string;
  refined_prompt?: string;
  compiled_steps?: string;
  trigger: string;
  schedule_cron?: string;
  status: string;
  run_count: number;
  last_run_at?: string;
  success_count: number;
  failure_count: number;
  created_by?: string;
  created_at: string;
}

export interface AutomationLog {
  id: number;
  workflow_id: number;
  status: string;
  input_data?: string;
  output_data?: string;
  error_message?: string;
  cost_usd: number;
  duration_seconds?: number;
  started_at: string;
  completed_at?: string;
}

export interface AccountsSummary {
  balance: number;
  total_credits: number;
  total_debits: number;
  this_month: { credits: number; debits: number; net: number };
  by_category: Record<string, { credits: number; debits: number; transactions: number }>;
}

// --- Core API functions ---
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

// --- Admin API functions ---
export const adminAuthApi = {
  login: (email: string, password: string) =>
    api.post<AdminLoginResponse>("/api/admin/auth/login", { email, password }),
  me: () => api.get<AdminUser>("/api/admin/auth/me"),
  changePassword: (current_password: string, new_password: string) =>
    api.post("/api/admin/auth/change-password", { current_password, new_password }),
  listUsers: () => api.get<AdminUser[]>("/api/admin/auth/users"),
  createUser: (data: { email: string; full_name: string; phone?: string; role?: UserRole; password: string }) =>
    api.post<AdminUser>("/api/admin/auth/users", data),
  deactivateUser: (id: number) => api.patch(`/api/admin/auth/users/${id}/deactivate`),
  activateUser: (id: number) => api.patch(`/api/admin/auth/users/${id}/activate`),
};

export const adminPipelineApi = {
  overview: () => api.get<PipelineOverview>("/api/admin/pipeline/overview"),
  leadVelocity: (days?: number) => api.get("/api/admin/pipeline/lead-velocity", { params: { days } }),
  conversionFunnel: () => api.get("/api/admin/pipeline/conversion-funnel"),
  topLeads: (limit?: number) => api.get("/api/admin/pipeline/top-leads", { params: { limit } }),
};

export const adminCostsApi = {
  overview: (days?: number) => api.get<CostOverview>("/api/admin/costs/overview", { params: { days } }),
  walletTopup: (amount: number, currency?: string) =>
    api.post("/api/admin/costs/wallet/topup", { amount, currency }),
  transactions: (params?: object) => api.get("/api/admin/costs/transactions", { params }),
  recordAiUsage: (data: object) => api.post("/api/admin/costs/ai-usage", data),
  listAiUsage: (params?: object) => api.get("/api/admin/costs/ai-usage", { params }),
  dailyBreakdown: (days?: number) => api.get("/api/admin/costs/daily-breakdown", { params: { days } }),
};

export const adminSettingsApi = {
  categories: () => api.get("/api/admin/settings/categories"),
  known: () => api.get("/api/admin/settings/known"),
  list: (category?: string) => api.get<SystemSettingItem[]>("/api/admin/settings", { params: { category } }),
  create: (data: { key: string; value: string; category?: string; is_secret?: boolean; description?: string }) =>
    api.post<SystemSettingItem>("/api/admin/settings", data),
  update: (key: string, value: string) => api.put<SystemSettingItem>(`/api/admin/settings/${key}`, { value }),
  delete: (key: string) => api.delete(`/api/admin/settings/${key}`),
  status: () => api.get("/api/admin/settings/status"),
};

export const adminAutomationsApi = {
  actions: () => api.get("/api/admin/automations/actions"),
  compile: (prompt: string) => api.post("/api/admin/automations/compile", { prompt }),
  list: (status?: string) => api.get<AutomationWorkflow[]>("/api/admin/automations", { params: { status } }),
  create: (data: { name: string; description?: string; natural_language_prompt: string; trigger?: string; schedule_cron?: string }) =>
    api.post<AutomationWorkflow>("/api/admin/automations", data),
  get: (id: number) => api.get<AutomationWorkflow>(`/api/admin/automations/${id}`),
  update: (id: number, data: object) => api.patch<AutomationWorkflow>(`/api/admin/automations/${id}`, data),
  activate: (id: number) => api.post(`/api/admin/automations/${id}/activate`),
  run: (id: number, input_data?: object) => api.post(`/api/admin/automations/${id}/run`, { input_data }),
  logs: (id: number, limit?: number) => api.get<AutomationLog[]>(`/api/admin/automations/${id}/logs`, { params: { limit } }),
  delete: (id: number) => api.delete(`/api/admin/automations/${id}`),
};

export const adminAccountsApi = {
  summary: () => api.get<AccountsSummary>("/api/admin/accounts/summary"),
  recordTransaction: (data: object) => api.post("/api/admin/accounts/transactions", data),
  transactions: (params?: object) => api.get("/api/admin/accounts/transactions", { params }),
  monthlyTrend: (months?: number) => api.get("/api/admin/accounts/monthly-trend", { params: { months } }),
};
