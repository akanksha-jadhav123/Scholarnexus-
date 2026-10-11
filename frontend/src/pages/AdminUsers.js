import React, { useEffect, useState } from "react";
import api from "../services/api";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const res = await api.get("/admin/users");
      setUsers(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const changeRole = async (userId, newRole) => {
    if (!window.confirm(`Change role to ${newRole}?`)) return;
    await api.put(`/admin/users/${userId}/role`, { role: newRole });
    load();
  };

  const filtered = users.filter(
    (u) =>
      u.name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="text-center py-5">Loading users...</div>;

  return (
    <div className="animate-in">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2 style={{ fontWeight: 800, margin: 0 }}>👥 Users</h2>
        <span className="badge bg-primary">{users.length} total</span>
      </div>

      <div className="sn-card mb-3">
        <input
          className="form-control"
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="sn-card">
        <div className="table-responsive">
          <table className="table table-sm align-middle mb-0">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Joined</th>
                <th>Bookmarks</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u._id}>
                  <td><strong>{u.name}</strong></td>
                  <td style={{ fontSize: "0.85rem" }}>{u.email}</td>
                  <td>
                    <span className={`badge ${u.role === "admin" ? "bg-danger" : "bg-primary"}`}>
                      {u.role}
                    </span>
                  </td>
                  <td style={{ fontSize: "0.8rem" }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}
                  </td>
                  <td>{(u.bookmarks || []).length}</td>
                  <td>
                    {u.role === "student" ? (
                      <button
                        className="btn btn-sm btn-outline-danger"
                        style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                        onClick={() => changeRole(u._id, "admin")}
                      >
                        Make Admin
                      </button>
                    ) : (
                      <button
                        className="btn btn-sm btn-outline-secondary"
                        style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                        onClick={() => changeRole(u._id, "student")}
                      >
                        Make Student
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}