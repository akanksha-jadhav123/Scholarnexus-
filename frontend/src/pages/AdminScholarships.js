import React, { useEffect, useState } from "react";
import api from "../services/api";

export default function AdminScholarships() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("Active");
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);

  useEffect(() => { load(); }, [statusFilter]);

  const load = async () => {
    setLoading(true);
    try {
      const params = { q: search };
      if (statusFilter) params.status = statusFilter;
      const res = await api.get("/scholarships/search", { params });
      setItems(res.data.results || []);
    } finally {
      setLoading(false);
    }
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
    await api.post(`/admin/scholarships/${id}/verify`);
    load();
  };

  const remove = async (id) => {
    if (!window.confirm(`Deactivate ${id}?`)) return;
    await api.delete(`/admin/scholarships/${id}`);
    load();
  };

  return (
    <div className="animate-in">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h2 style={{ fontWeight: 800, margin: 0 }}>📚 Manage Scholarships</h2>
        <span className="badge bg-primary">{items.length} records</span>
      </div>

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
            <select className="form-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
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

      {loading ? (
        <div className="text-center py-4">Loading...</div>
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
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => (
                  <tr key={s.scholarship_id}>
                    <td><code style={{ fontSize: "0.75rem" }}>{s.scholarship_id}</code></td>
                    <td title={s.scholarship_name}>
                      {s.scholarship_name?.slice(0, 40)}{s.scholarship_name?.length > 40 ? "..." : ""}
                    </td>
                    <td>{s.provider?.slice(0, 20)}</td>
                    <td>
                      <span className="badge bg-secondary" style={{ fontSize: "0.7rem" }}>
                        {s.source || "-"}
                      </span>
                    </td>
                    <td>{s.scholarship_amount ? `₹${s.scholarship_amount.toLocaleString()}` : "-"}</td>
                    <td>{s.application_deadline || "-"}</td>
                    <td>
                      <span className={`badge ${
                        s.status === "Active" ? "bg-success" :
                        s.status === "Expired" ? "bg-secondary" : "bg-warning"
                      }`}>
                        {s.status}
                      </span>
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        <button
                          className="btn btn-sm btn-outline-success"
                          title="Verify"
                          onClick={() => verify(s.scholarship_id)}
                          style={{ fontSize: "0.7rem", padding: "2px 6px" }}
                        >
                          ✓
                        </button>
                        {s.status === "Active" ? (
                          <button
                            className="btn btn-sm btn-outline-warning"
                            onClick={() => deactivate(s.scholarship_id)}
                            style={{ fontSize: "0.7rem", padding: "2px 6px" }}
                          >
                            Deactivate
                          </button>
                        ) : (
                          <button
                            className="btn btn-sm btn-outline-success"
                            onClick={() => activate(s.scholarship_id)}
                            style={{ fontSize: "0.7rem", padding: "2px 6px" }}
                          >
                            Activate
                          </button>
                        )}
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => remove(s.scholarship_id)}
                          style={{ fontSize: "0.7rem", padding: "2px 6px" }}
                        >
                          Deactivate
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