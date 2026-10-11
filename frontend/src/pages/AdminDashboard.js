import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);       // full error object
  const [debug, setDebug] = useState({});

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    setError(null);

    // Capture what the browser has
    const token = localStorage.getItem("token");
    const user = localStorage.getItem("user");
    const apiBase = process.env.REACT_APP_API_BASE_URL;

    setDebug({
      token: token ? `${token.slice(0, 30)}...` : "MISSING",
      user: user || "MISSING",
      apiBase: apiBase || "MISSING",
    });

    if (!token) {
      setError({ message: "No token found — please log in again." });
      setLoading(false);
      return;
    }

    try {
      const res = await api.get("/admin/analytics");
      setStats(res.data);
    } catch (e) {
      // Capture EVERYTHING
      setError({
        message: e.message || "Unknown error",
        status: e.response?.status,
        statusText: e.response?.statusText,
        url: e.config?.url,
        method: e.config?.method,
        baseURL: e.config?.baseURL,
        serverResponse: e.response?.data,
        isNetworkError: !e.response,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-5">Loading admin data...</div>;

  if (error) {
    return (
      <div className="container py-5">
        <div className="sn-card">
          <h3 style={{ color: "#dc3545", fontWeight: 800, marginBottom: "16px" }}>
            ⚠️ Analytics Failed
          </h3>

          <p style={{ fontSize: "1.05rem", marginBottom: "20px" }}>
            <strong>Error:</strong> {error.message}
          </p>

          <div style={{
            background: "#f8fafc",
            padding: "20px",
            borderRadius: "12px",
            marginBottom: "20px",
            fontFamily: "monospace",
            fontSize: "0.85rem"
          }}>
            <div><strong>HTTP Status:</strong> {error.status || "N/A (network error)"}</div>
            <div><strong>Request URL:</strong> {error.baseURL}{error.url}</div>
            <div><strong>Method:</strong> {error.method?.toUpperCase()}</div>
            {error.serverResponse && (
              <div style={{ marginTop: "10px" }}>
                <strong>Server response:</strong>
                <pre style={{ margin: "6px 0", whiteSpace: "pre-wrap" }}>
                  {JSON.stringify(error.serverResponse, null, 2)}
                </pre>
              </div>
            )}
          </div>

          <div style={{
            background: "#eff6ff",
            padding: "16px",
            borderRadius: "12px",
            marginBottom: "20px",
            fontSize: "0.85rem"
          }}>
            <strong>Debug info:</strong>
            <div>Token: <code>{debug.token}</code></div>
            <div>User: <code>{debug.user}</code></div>
            <div>API Base: <code>{debug.apiBase}</code></div>
          </div>

          <div className="d-flex gap-2 flex-wrap">
            <button className="btn-sn" onClick={load}>🔄 Try Again</button>
            <button
              className="btn-sn-outline"
              onClick={() => {
                localStorage.clear();
                window.location.href = "/login";
              }}
            >
              Clear Session & Re-login
            </button>
            <Link to="/" className="btn-sn-ghost" style={{ textDecoration: "none" }}>
              Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  // ===================== NORMAL RENDER =====================
  return (
    <div className="animate-in">
      <div className="sn-card mb-4" style={{
        background: "linear-gradient(135deg, #4f46e5, #0ea5e9)",
        color: "white", border: "none"
      }}>
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h2 style={{ fontWeight: 800, marginBottom: "8px" }}>🛠️ Admin Dashboard</h2>
            <p style={{ opacity: 0.9, marginBottom: 0 }}>
              Full platform overview • Generated {new Date(stats.generated_at).toLocaleString()}
            </p>
          </div>
          <button className="btn-sn" onClick={load} style={{ background: "white", color: "var(--primary)" }}>
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon primary">👥</div>
            <div>
              <div className="stat-value">{stats.users.students}</div>
              <div className="stat-label">Students</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon success">🎓</div>
            <div>
              <div className="stat-value">{stats.scholarships.total}</div>
              <div className="stat-label">Scholarships</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon warning">📋</div>
            <div>
              <div className="stat-value">{stats.applications.total}</div>
              <div className="stat-label">Applications</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon danger">🔖</div>
            <div>
              <div className="stat-value">{stats.bookmarks}</div>
              <div className="stat-label">Bookmarks</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <Link to="/admin/scholarships" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2.5rem", marginBottom: "10px" }}>📚</div>
            <strong style={{ color: "var(--dark)", fontSize: "1.1rem" }}>Scholarships</strong>
            <p style={{ margin: "6px 0 0", fontSize: "0.85rem", color: "var(--gray)" }}>
              {stats.scholarships.total} records • Add, edit, delete
            </p>
          </Link>
        </div>
        <div className="col-md-4">
          <Link to="/admin/sources" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2.5rem", marginBottom: "10px" }}>📡</div>
            <strong style={{ color: "var(--dark)", fontSize: "1.1rem" }}>Sources & Scraper</strong>
            <p style={{ margin: "6px 0 0", fontSize: "0.85rem", color: "var(--gray)" }}>
              Manage scrapers • Run sync
            </p>
          </Link>
        </div>
        <div className="col-md-4">
          <Link to="/admin/users" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2.5rem", marginBottom: "10px" }}>👥</div>
            <strong style={{ color: "var(--dark)", fontSize: "1.1rem" }}>Users</strong>
            <p style={{ margin: "6px 0 0", fontSize: "0.85rem", color: "var(--gray)" }}>
              {stats.users.students + stats.users.admins} total • Manage roles
            </p>
          </Link>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-md-6">
          <div className="sn-card h-100">
            <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>📊 Scholarships by Source</h5>
            <table className="table table-sm mb-0">
              <thead><tr><th>Source</th><th className="text-end">Count</th></tr></thead>
              <tbody>
                {Object.entries(stats.scholarships.by_source || {}).map(([s, c]) => (
                  <tr key={s}>
                    <td>{s}</td>
                    <td className="text-end"><strong>{c}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="col-md-6">
          <div className="sn-card h-100">
            <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>👥 Scholarships by Category</h5>
            <table className="table table-sm mb-0">
              <thead><tr><th>Category</th><th className="text-end">Count</th></tr></thead>
              <tbody>
                {Object.entries(stats.scholarships.by_category || {}).map(([s, c]) => (
                  <tr key={s}>
                    <td>{s}</td>
                    <td className="text-end"><strong>{c}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="sn-card mt-3">
        <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>🔗 Link Health</h5>
        <div className="row g-3">
          <div className="col-md-4">
            <div style={{ background: "#ecfdf5", padding: "14px", borderRadius: "10px" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#065f46" }}>
                {stats.link_health.active}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#065f46" }}>Active links</div>
            </div>
          </div>
          <div className="col-md-4">
            <div style={{ background: "#fef3c7", padding: "14px", borderRadius: "10px" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#92400e" }}>
                {stats.link_health.pending}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#92400e" }}>Pending validation</div>
            </div>
          </div>
          <div className="col-md-4">
            <div style={{ background: "#fef2f2", padding: "14px", borderRadius: "10px" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#991b1b" }}>
                {stats.link_health.broken}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#991b1b" }}>Broken links</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}