"use client";
import { useEffect, useState } from "react";
import { adminSettingsApi, SystemSettingItem } from "@/lib/api";

const CATEGORY_ICONS: Record<string, string> = {
  ai: "🤖", outreach: "📨", crm: "📊", storage: "☁️", scraping: "🕷️", social: "📱", payments: "💳", general: "⚙️",
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettingItem[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [categories, setCategories] = useState<Record<string, string>>({});
  const [activeCategory, setActiveCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [newCategory, setNewCategory] = useState("general");
  const [newIsSecret, setNewIsSecret] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      adminSettingsApi.list(activeCategory || undefined),
      adminSettingsApi.status(),
      adminSettingsApi.categories(),
    ])
      .then(([settingsRes, statusRes, catsRes]) => {
        setSettings(settingsRes.data);
        setStatus(statusRes.data);
        setCategories(catsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [activeCategory]);

  const handleSave = async () => {
    if (!newKey || !newValue) return;
    setSaving(true);
    try {
      await adminSettingsApi.create({ key: newKey, value: newValue, category: newCategory, is_secret: newIsSecret });
      setShowAddModal(false);
      setNewKey("");
      setNewValue("");
      fetchData();
    } catch (err) {
      alert("Failed to save setting");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (key: string) => {
    if (!confirm(`Delete setting "${key}"?`)) return;
    await adminSettingsApi.delete(key);
    fetchData();
  };

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Settings & Integrations</h1>
            <p className="text-sm text-gray-500 mt-0.5">Manage API keys, secrets, and system configuration</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            + Add Setting
          </button>
        </div>
      </header>

      <div className="p-8 space-y-6">
        {/* Status Overview */}
        {status && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Integration Status</h3>
            <div className="flex items-center gap-6 mb-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{status.configured}</p>
                <p className="text-xs text-gray-500">Configured</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-500">{status.missing}</p>
                <p className="text-xs text-gray-500">Missing</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-400">{status.total_known}</p>
                <p className="text-xs text-gray-500">Total Known</p>
              </div>
              <div className="flex-1">
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all"
                    style={{ width: `${(status.configured / status.total_known) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">{Math.round((status.configured / status.total_known) * 100)}% configured</p>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
              {Object.entries(status.details || {}).map(([key, detail]: [string, any]) => (
                <div
                  key={key}
                  className={`text-xs px-3 py-2 rounded-lg border ${
                    detail.configured
                      ? "bg-green-50 border-green-200 text-green-700"
                      : "bg-red-50 border-red-200 text-red-600"
                  }`}
                >
                  <span className="font-medium">{detail.configured ? "✓" : "✗"}</span>{" "}
                  {key.replace(/_/g, " ")}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category Filter */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setActiveCategory("")}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              !activeCategory ? "bg-blue-600 text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            All
          </button>
          {Object.entries(categories).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActiveCategory(key)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeCategory === key ? "bg-blue-600 text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
              }`}
            >
              {CATEGORY_ICONS[key] || "📌"} {label}
            </button>
          ))}
        </div>

        {/* Settings List */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-white rounded-xl animate-pulse" />)}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Key</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Value</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Category</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Updated</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {settings.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-800">{s.key}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-500 max-w-xs truncate">
                      {s.is_secret ? <span className="text-gray-400">{s.value}</span> : s.value}
                      {s.is_secret && <span className="ml-2 text-[10px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">SECRET</span>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full capitalize">{s.category}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">
                      {new Date(s.updated_at).toLocaleDateString()}
                      {s.updated_by && <span className="block text-[10px]">by {s.updated_by}</span>}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button onClick={() => handleDelete(s.key)} className="text-red-400 hover:text-red-600 text-xs transition-colors">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {settings.length === 0 && <p className="text-center py-8 text-gray-400 text-sm">No settings configured.</p>}
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add Setting</h3>
            <div className="space-y-3">
              <input
                placeholder="Setting key (e.g. anthropic_api_key)"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <input
                placeholder="Value"
                type={newIsSecret ? "password" : "text"}
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              >
                {Object.entries(categories).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
              <label className="flex items-center gap-2 text-sm text-gray-600">
                <input type="checkbox" checked={newIsSecret} onChange={(e) => setNewIsSecret(e.target.checked)} className="rounded" />
                Secret value (masked in UI)
              </label>
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={() => setShowAddModal(false)} className="flex-1 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={handleSave} disabled={saving} className="flex-1 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
                {saving ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
