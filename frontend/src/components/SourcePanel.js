import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function SourcePanel() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [sources, setSources] = useState([]);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const [s, src] = await Promise.all([
        api.get("/scraper/stats"),
        api.get("/scraper/sources")
      ]);
      setStats(s.data);
      setSources(src.data);
    } catch (e) {}
  };

  if (user?.role !== "admin" || !stats) return null;

  return (
    <div className="sn-card mb-4">
      <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>📡 Multi-Source Aggregation</h5>

      <div className="row g-3 mb-3">
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon primary">🗄️</div>
            <div>
              <div className="stat-value">{stats.db_total}</div>
              <div className="stat-label">Total</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon success">✅</div>
            <div>
              <div className="stat-value">{stats.link_stats.active}</div>
              <div className="stat-label">Links OK</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon danger">🔗</div>
            <div>
              <div className="stat-value">{stats.link_stats.broken}</div>
              <div className="stat-label">Broken</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon warning">📡</div>
            <div>
              <div className="stat-value">{stats.sources_registered}</div>
              <div className="stat-label">Sources</div>
            </div>
          </div>
        </div>
      </div>

      <h6 style={{ fontWeight: 700, marginTop: "16px" }}>Registered Sources</h6>
      <div className="row g-2">
        {sources.map((s, i) => (
          <div className="col-md-6" key={i}>
            <div style={{ padding: "10px 14px", background: "var(--light)", borderRadius: "10px" }}>
              <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{s.name}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--gray)" }}>
                {s.url} • {s.delay_seconds}s delay
              </div>
            </div>
          </div>
        ))}
      </div>

      <h6 style={{ fontWeight: 700, marginTop: "16px" }}>Records by Source</h6>
      <table className="table table-sm">
        <thead>
          <tr><th>Source</th><th>Count</th></tr>
        </thead>
        <tbody>
          {Object.entries(stats.by_source || {}).map(([source, count]) => (
            <tr key={source}>
              <td>{source}</td>
              <td><strong>{count}</strong></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}