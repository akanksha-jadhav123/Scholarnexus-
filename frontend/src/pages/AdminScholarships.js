import React, { useEffect, useState } from "react";
import api, { deleteScholarship } from "../services/api";
import ManualScholarshipForm from "../components/ManualScholarshipForm";

export default function AdminScholarships() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("Active");
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);

  useEffect(() => { load(); }, [statusFilter]);

  const load = async () => {
    setLoading(true);
    try {
      const params = { q: search };
      if (statusFilter) params.status = statusFilter;
      const res = await api.get("/scholarships/search", { params });
      setItems(res.data.results || []);
    } catch (e) {
      console.error("Load failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditing(null);
    setShowForm(true);
  };

  const handleEdit = (scholarship) => {
    setEditing(scholarship);
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditing(null);
    load();
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditing(null);
  };

  const deactivate = async (id) => {
    if (!window.confirm(`Deactivate ${id}?`)) return;
    await api.put(`/scholarships/${id}`, { status: "Inactive" });
    load();
  };

  const activate = async (id) => {
    await api.put(`/scholarships/${id}`, { status: "Active" });
    load();
  };

  const verify = async (id) => {
    try {
      await api.post(`/admin/scholarships/${id}/verify`);
      load();
    } catch (e) {
      alert(e.response?.data?.error || "Verify failed");
    }
  };

  const hardDelete = async (id) => {
    if (!window.confirm(
      `⚠️ PERMANENTLY DELETE ${id}?\n\nThis cannot be undone.`
    )) return;
    try {
      await deleteScholarship(id);
      load();
    } catch (e) {
      alert(e.response?.data?.error || "Delete failed");
    }
  };

  return (
    <div className="animate-in">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h2 style={{ fontWeight: 800, margin: 0 }}>📚 Manage Scholarships</h2>
        <div className="d-flex gap-2 align-items-center">
          <span className="badge bg-primary">{items.length} records</span>
          <button className="btn-sn" onClick={handleCreate}>
            ➕ Add Scholarship
          </button>
        </div>
      </div>

      {/* MANUAL ENTRY FORM */}
      {showForm && (
        <ManualScholarshipForm
          editData={editing}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      )}

      {/* SEARCH */}
      <div className="sn-card mb-3">
        <div className="row g-2">
          <div className="col-md-6">
            <input
              className="form-control"
              placeholder="Search by name or provider..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && load()}
            />
          </div>
          <div className="col-md-3">
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All statuses</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Expired">Expired</option>
            </select>
          </div>
          <div className="col-md-3">
            <button className="btn-sn w-100" onClick={load}>Search</button>
          </div>
        </div>
      </div>

      {/* TABLE */}
      {loading ? (
        <div className="text-center py-4">Loading...</div>
      ) : items.length === 0 ? (
        <div className="sn-card text-center py-5">
          <div style={{ fontSize: "3rem" }}>📭</div>
          <p className="text-muted mb-3">No scholarships found.</p>
          <button className="btn-sn" onClick={handleCreate}>
            ➕ Add the first one
          </button>
        </div>
      ) : (
        <div className="sn-card">
          <div className="table-responsive">
            <table className="table table-sm align-middle mb-0">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Provider</th>
                  <th>Source</th>
                  <th>Amount</th>
                  <th>Deadline</th>
                  <th>Status</th>
                  <th style={{ minWidth: "230px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => (
                  <tr key={s.scholarship_id}>
                    <td>
                      <code style={{ fontSize: "0.72rem" }}>{s.scholarship_id}</code>
                    </td>
                    <td title={s.scholarship_name} style={{ maxWidth: "220px" }}>
                      {s.scholarship_name?.slice(0, 40)}
                      {s.scholarship_name?.length > 40 ? "…" : ""}
                    </td>
                    <td style={{ fontSize: "0.85rem" }}>
                      {s.provider?.slice(0, 25)}
                    </td>
                    <td>
                      <span className="badge bg-secondary" style={{ fontSize: "0.68rem" }}>
                        {s.source || "—"}
                      </span>
                    </td>
                    <td style={{ fontSize: "0.85rem" }}>
                      {s.scholarship_amount
                        ? `₹${Number(s.scholarship_amount).toLocaleString("en-IN")}`
                        : "—"}
                    </td>
                    <td style={{ fontSize: "0.85rem" }}>
                      {s.application_deadline || "—"}
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          s.status === "Active"
                            ? "bg-success"
                            : s.status === "Expired"
                            ? "bg-secondary"
                            : "bg-warning text-dark"
                        }`}
                      >
                        {s.status}
                      </span>
                    </td>
                    <td>
                      <div className="d-flex gap-1 flex-wrap">
                        <button
                          className="btn btn-sm btn-outline-primary"
                          title="Edit"
                          onClick={() => handleEdit(s)}
                          style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                        >
                          ✏️ Edit
                        </button>
                        <button
                          className="btn btn-sm btn-outline-success"
                          title="Mark verified"
                          onClick={() => verify(s.scholarship_id)}
                          style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                        >
                          ✓
                        </button>
                        {s.status === "Active" ? (
                          <button
                            className="btn btn-sm btn-outline-warning"
                            onClick={() => deactivate(s.scholarship_id)}
                            style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                          >
                            ⏸ Deactivate
                          </button>
                        ) : (
                          <button
                            className="btn btn-sm btn-outline-success"
                            onClick={() => activate(s.scholarship_id)}
                            style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                          >
                            ▶ Activate
                          </button>
                        )}
                        <button
                          className="btn btn-sm btn-outline-danger"
                          title="Permanently delete"
                          onClick={() => hardDelete(s.scholarship_id)}
                          style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                        >
                          🗑 Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}