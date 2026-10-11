import React, { useEffect, useState } from "react";
import api from "../services/api";

export default function AdminSources() {
  const [sources, setSources] = useState([]);
  const [stats, setStats] = useState(null);
  const [running, setRunning] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const [srcRes, statsRes] = await Promise.all([
        api.get("/crawler/sources").catch(() => ({ data: [] })),
        api.get("/crawler/stats").catch(() => ({ data: null }))
      ]);

      const data = srcRes.data;
      let list = [];
      if (Array.isArray(data)) list = data;
      else if (data?.all && Array.isArray(data.all)) list = data.all;
      else if (data?.sources && Array.isArray(data.sources)) list = data.sources;

      setSources(list);
      setStats(statsRes.data);
    } finally {
      setLoading(false);
    }
  };

  const runSync = async () => {
    setRunning(true);
    setLastResult(null);
    try {
      const res = await api.post("/crawler/sync");
      setLastResult(res.data.stats);
      await load();
    } catch (err) {
      alert(err.response?.data?.error || "Sync failed");
    } finally {
      setRunning(false);
    }
  };

  if (loading) return <div className="text-center py-5">Loading...</div>;

  return (
    <div className="animate-in">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h2 style={{ fontWeight: 800, margin: 0 }}>📡 Sources & Scraper</h2>
        <button className="btn-sn" onClick={runSync} disabled={running}>
          {running ? "⏳ Running..." : "▶ Run Sync Now"}
        </button>
      </div>

      {/* STATS */}
      {stats && (
        <div className="row g-3 mb-4">
          <div className="col-md-4">
            <div className="stat-card">
              <div className="stat-icon primary">🗄️</div>
              <div>
                <div className="stat-value">{stats.db_total || 0}</div>
                <div className="stat-label">Total Records</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="stat-card">
              <div className="stat-icon success">📡</div>
              <div>
                <div className="stat-value">{sources.length}</div>
                <div className="stat-label">Registered Sources</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="stat-card">
              <div className="stat-icon warning">⏰</div>
              <div>
                <div className="stat-value" style={{ fontSize: "1.2rem" }}>
                  {stats.last_sync?.at
                    ? new Date(stats.last_sync.at).toLocaleDateString()
                    : "Never"}
                </div>
                <div className="stat-label">Last Sync</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* LAST RESULT */}
      {lastResult && (
        <div className="alert alert-success">
          ✅ <strong>Sync complete:</strong>{" "}
          crawled <strong>{lastResult.crawled || lastResult.total_crawled || 0}</strong>,
          saved <strong>{lastResult.saved || lastResult.total_saved || 0}</strong>,
          duplicates <strong>{lastResult.duplicates || lastResult.total_duplicates || 0}</strong>,
          rejected <strong>{lastResult.rejected || lastResult.total_rejected || 0}</strong>
        </div>
      )}

      {/* SOURCES LIST */}
      <div className="sn-card mb-3">
        <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>
          Registered Sources ({sources.length})
        </h5>
        {sources.length === 0 ? (
          <p className="text-muted">No sources returned by backend.</p>
        ) : (
          <div className="row g-2">
            {sources.map((s, i) => (
              <div className="col-md-6" key={i}>
                <div style={{
                  padding: "12px 14px",
                  background: "var(--light)",
                  borderRadius: "10px",
                  borderLeft: "3px solid var(--primary)"
                }}>
                  <div style={{ fontWeight: 700, fontSize: "0.95rem" }}>
                    {s.name || s.source_name || "Unknown"}
                  </div>
                  <div style={{ fontSize: "0.78rem", color: "var(--gray)", wordBreak: "break-all" }}>
                    {s.url || s.base_url || "-"}
                  </div>
                  {s.type && (
                    <span className="badge bg-secondary mt-1" style={{ fontSize: "0.7rem" }}>
                      {s.type}
                    </span>
                  )}
                  {s.trust_score && (
                    <span className="badge bg-info text-dark mt-1 ms-1" style={{ fontSize: "0.7rem" }}>
                      Trust: {s.trust_score}/10
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RECORDS BY SOURCE */}
      {stats?.by_source && Object.keys(stats.by_source).length > 0 && (
        <div className="sn-card">
          <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>📊 Records by Source</h5>
          <table className="table table-sm mb-0">
            <thead>
              <tr>
                <th>Source</th>
                <th className="text-end">Records</th>
                <th className="text-end">Share</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(stats.by_source)
                .sort((a, b) => b[1] - a[1])
                .map(([s, c]) => {
                  const pct = stats.db_total ? Math.round((c / stats.db_total) * 100) : 0;
                  return (
                    <tr key={s}>
                      <td>{s}</td>
                      <td className="text-end"><strong>{c}</strong></td>
                      <td className="text-end">{pct}%</td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}