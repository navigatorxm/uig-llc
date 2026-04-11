"use client";
import { useEffect, useState } from "react";
import { adminAutomationsApi, AutomationWorkflow } from "@/lib/api";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  active: "bg-green-50 text-green-700",
  paused: "bg-yellow-50 text-yellow-700",
  archived: "bg-red-50 text-red-500",
};

export default function AutomationsPage() {
  const [workflows, setWorkflows] = useState<AutomationWorkflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [compileResult, setCompileResult] = useState<any>(null);
  const [newName, setNewName] = useState("");
  const [newPrompt, setNewPrompt] = useState("");
  const [newTrigger, setNewTrigger] = useState("manual");
  const [saving, setSaving] = useState(false);
  const [compiling, setCompiling] = useState(false);
  const [runningId, setRunningId] = useState<number | null>(null);

  const fetchWorkflows = () => {
    setLoading(true);
    adminAutomationsApi.list()
      .then((r) => setWorkflows(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchWorkflows(); }, []);

  const handleCompile = async () => {
    if (!newPrompt) return;
    setCompiling(true);
    try {
      const { data } = await adminAutomationsApi.compile(newPrompt);
      setCompileResult(data);
    } catch { alert("Compile failed"); }
    finally { setCompiling(false); }
  };

  const handleCreate = async () => {
    if (!newName || !newPrompt) return;
    setSaving(true);
    try {
      await adminAutomationsApi.create({
        name: newName,
        natural_language_prompt: newPrompt,
        trigger: newTrigger,
      });
      setShowCreate(false);
      setNewName("");
      setNewPrompt("");
      setCompileResult(null);
      fetchWorkflows();
    } catch { alert("Failed to create workflow"); }
    finally { setSaving(false); }
  };

  const handleRun = async (id: number) => {
    setRunningId(id);
    try {
      const { data } = await adminAutomationsApi.run(id);
      alert(`Workflow executed: ${data.status}${data.error ? ` — ${data.error}` : ""}`);
      fetchWorkflows();
    } catch { alert("Execution failed"); }
    finally { setRunningId(null); }
  };

  const handleActivate = async (id: number) => {
    await adminAutomationsApi.activate(id);
    fetchWorkflows();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this workflow?")) return;
    await adminAutomationsApi.delete(id);
    fetchWorkflows();
  };

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Automations</h1>
            <p className="text-sm text-gray-500 mt-0.5">AI-powered workflow engine — describe tasks in plain English</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-500 text-white text-sm font-medium rounded-lg hover:from-blue-500 hover:to-cyan-400 transition-all shadow-lg shadow-blue-500/25"
          >
            + New Automation
          </button>
        </div>
      </header>

      <div className="p-8 space-y-6">
        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-white rounded-xl animate-pulse" />)}
          </div>
        ) : workflows.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-100 shadow-sm">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-800">No automations yet</h3>
            <p className="text-sm text-gray-500 mt-1 max-w-sm mx-auto">
              Create your first workflow by describing what you want in plain English.
            </p>
            <button
              onClick={() => setShowCreate(true)}
              className="mt-4 px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Automation
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {workflows.map((wf) => (
              <div key={wf.id} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-800">{wf.name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${STATUS_COLORS[wf.status] || "bg-gray-100 text-gray-500"}`}>
                        {wf.status}
                      </span>
                      <span className="text-xs bg-gray-50 text-gray-500 px-2 py-0.5 rounded-full capitalize">{wf.trigger}</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-2">{wf.natural_language_prompt}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Runs: {wf.run_count}</span>
                      <span className="text-green-500">✓ {wf.success_count}</span>
                      <span className="text-red-400">✗ {wf.failure_count}</span>
                      {wf.last_run_at && <span>Last: {new Date(wf.last_run_at).toLocaleDateString()}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {wf.status === "draft" && (
                      <button onClick={() => handleActivate(wf.id)} className="px-3 py-1.5 text-xs font-medium bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors">
                        Activate
                      </button>
                    )}
                    <button
                      onClick={() => handleRun(wf.id)}
                      disabled={runningId === wf.id}
                      className="px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
                    >
                      {runningId === wf.id ? "Running..." : "Run Now"}
                    </button>
                    <button onClick={() => handleDelete(wf.id)} className="px-3 py-1.5 text-xs text-red-400 hover:text-red-600 transition-colors">
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-gray-900 mb-4">New Automation</h3>
            <div className="space-y-4">
              <input
                placeholder="Workflow name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <div>
                <label className="text-xs font-medium text-gray-600 mb-1 block">Describe the automation in plain English:</label>
                <textarea
                  placeholder="e.g., When a new lead comes in, score them using AI, then send a WhatsApp greeting. If no response in 24 hours, follow up via email."
                  value={newPrompt}
                  onChange={(e) => setNewPrompt(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 resize-none"
                />
              </div>
              <select
                value={newTrigger}
                onChange={(e) => setNewTrigger(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              >
                <option value="manual">Manual</option>
                <option value="new_lead">New Lead</option>
                <option value="stage_change">Stage Change</option>
                <option value="schedule">Scheduled (Cron)</option>
                <option value="webhook">Webhook</option>
              </select>

              <button
                onClick={handleCompile}
                disabled={compiling || !newPrompt}
                className="w-full py-2 text-sm bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors font-medium disabled:opacity-50"
              >
                {compiling ? "Compiling..." : "🔮 Preview Compiled Steps"}
              </button>

              {compileResult && (
                <div className="bg-gray-50 rounded-lg p-3 text-xs">
                  <p className="font-medium text-gray-700 mb-2">Compiled into {compileResult.step_count} step(s):</p>
                  <div className="space-y-1">
                    {compileResult.compiled_steps?.map((step: any, i: number) => (
                      <div key={i} className="flex items-center gap-2 text-gray-600">
                        <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] font-bold flex-shrink-0">{i + 1}</span>
                        <span className="capitalize">{step.action.replace(/_/g, " ")}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={() => { setShowCreate(false); setCompileResult(null); }} className="flex-1 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={handleCreate} disabled={saving || !newName || !newPrompt} className="flex-1 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
                {saving ? "Creating..." : "Create Workflow"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
