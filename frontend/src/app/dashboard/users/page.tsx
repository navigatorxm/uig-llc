"use client";
import { useEffect, useState } from "react";
import { adminAuthApi, AdminUser, UserRole } from "@/lib/api";

const ROLE_COLORS: Record<string, string> = {
  master_admin: "bg-purple-50 text-purple-700 border-purple-200",
  admin: "bg-blue-50 text-blue-700 border-blue-200",
  sub_agent: "bg-gray-100 text-gray-600 border-gray-200",
};

export default function UsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [newRole, setNewRole] = useState<UserRole>("sub_agent");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchUsers = () => {
    setLoading(true);
    adminAuthApi.listUsers()
      .then((r) => setUsers(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async () => {
    if (!newEmail || !newName || !newPassword) return;
    setSaving(true);
    try {
      await adminAuthApi.createUser({
        email: newEmail,
        full_name: newName,
        phone: newPhone || undefined,
        role: newRole,
        password: newPassword,
      });
      setShowCreate(false);
      setNewEmail("");
      setNewName("");
      setNewPhone("");
      setNewPassword("");
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create user");
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (user: AdminUser) => {
    if (user.is_active) {
      await adminAuthApi.deactivateUser(user.id);
    } else {
      await adminAuthApi.activateUser(user.id);
    }
    fetchUsers();
  };

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Team & Users</h1>
            <p className="text-sm text-gray-500 mt-0.5">Manage admin users, roles, and access</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            + Add User
          </button>
        </div>
      </header>

      <div className="p-8">
        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => <div key={i} className="h-20 bg-white rounded-xl animate-pulse" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {users.map((user) => (
              <div key={user.id} className={`bg-white rounded-xl p-5 shadow-sm border transition-all hover:shadow-md ${user.is_active ? "border-gray-100" : "border-red-100 opacity-60"}`}>
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">{user.full_name.charAt(0).toUpperCase()}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-800 truncate">{user.full_name}</p>
                    <p className="text-xs text-gray-500 truncate">{user.email}</p>
                    {user.phone && <p className="text-xs text-gray-400">{user.phone}</p>}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-50">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border capitalize ${ROLE_COLORS[user.role] || ROLE_COLORS.sub_agent}`}>
                      {user.role.replace("_", " ")}
                    </span>
                    <span className={`text-xs ${user.is_active ? "text-green-600" : "text-red-500"}`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                  <button
                    onClick={() => handleToggle(user)}
                    className={`text-xs px-3 py-1 rounded-lg transition-colors ${
                      user.is_active
                        ? "text-red-500 hover:bg-red-50"
                        : "text-green-600 hover:bg-green-50"
                    }`}
                  >
                    {user.is_active ? "Deactivate" : "Activate"}
                  </button>
                </div>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-gray-400">
                  <span>Logins: {user.login_count}</span>
                  {user.last_login_at && <span>Last: {new Date(user.last_login_at).toLocaleDateString()}</span>}
                  <span>Joined: {new Date(user.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
        {!loading && users.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <p className="text-sm">No users found. Master admins are seeded on first startup.</p>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add Team Member</h3>
            <div className="space-y-3">
              <input
                placeholder="Full name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <input
                placeholder="Email address"
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <input
                placeholder="Phone (optional)"
                value={newPhone}
                onChange={(e) => setNewPhone(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <input
                placeholder="Initial password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
              />
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value as UserRole)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              >
                <option value="sub_agent">Sub Agent</option>
                <option value="admin">Admin</option>
                <option value="master_admin">Master Admin</option>
              </select>
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={() => setShowCreate(false)} className="flex-1 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={handleCreate} disabled={saving || !newEmail || !newName || !newPassword} className="flex-1 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
                {saving ? "Adding..." : "Add User"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
