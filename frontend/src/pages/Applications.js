import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listApplications, saveApplication, deleteApplication } from "../services/api";

const STATUSES = ["Interested", "Preparing", "Documents Pending",
                  "Applied", "Under Review", "Approved", "Rejected", "Expired"];

export default function Applications() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const res = await listApplications();
      setApps(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (sid, status) => {
    await saveApplication({ scholarship_id: sid, status });
    load();
  };

  const remove = async (sid) => {
    if (!window.confirm("Remove this application?")) return;
    await deleteApplication(sid);
    load();
  };

  if (loading) return <div className="text-center py-5">Loading applications...</div>;

  return (
    <div className="animate-in">
      <h2 style={{ fontWeight: 800, marginBottom: "16px" }}>📋 My Applications</h2>

      {apps.length === 0 ? (
        <div className="sn-card text-center py-5">
          <div style={{ fontSize: "3rem" }}>📭</div>
          <p style={{ color: "var(--gray)" }}>No applications yet.</p>
          <Link to="/scholarships" className="btn-sn">Browse Scholarships</Link>
        </div>
      ) : (
        apps.map((app) => (
          <div className="sn-card mb-3" key={app.scholarship_id}>
            <div className="d-flex justify-content-between flex-wrap gap-3">
              <div style={{ flex: 1 }}>
                <Link to={`/scholarships/${app.scholarship_id}`}
                  style={{ fontWeight: 700, textDecoration: "none", color: "var(--dark)" }}>
                  {app.scholarship_name || app.scholarship_id}
                </Link>
                <p style={{ margin: "4px 0", color: "var(--gray)", fontSize: "0.9rem" }}>
                  {app.provider} • Deadline: {app.application_deadline || "N/A"}
                </p>
                <span className="status-badge status-eligible">{app.status}</span>
              </div>
              <div className="d-flex gap-2">
                <select
                  className="form-select form-select-sm"
                  value={app.status}
                  onChange={(e) => updateStatus(app.scholarship_id, e.target.value)}
                  style={{ width: "auto" }}
                >
                  {STATUSES.map((s) => <option key={s}>{s}</option>)}
                </select>
                <button className="btn-sn-ghost" onClick={() => remove(app.scholarship_id)}>
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}