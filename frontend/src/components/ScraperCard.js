import React, { useState, useEffect } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function ScraperCard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => { loadStats(); }, []);

  const loadStats = async () => {
    try {
      const res = await api.get("/scraper/stats");
      setStats(res.data);
    } catch (e) {}
  };

  const trigger = async () => {
    setRunning(true);
    setResult(null);
    try {
      const res = await api.post("/scraper/run");
      setResult(res.data.stats);
      loadStats();
    } catch (err) {
      setResult({ error: err.response?.data?.error || "Failed" });
    } finally {
      setRunning(false);
    }
  };

  if (user?.role !== "admin") return null;

  return (
    <div className="sn-card mb-4">
      <h5 style={{ fontWeight: 700, marginBottom: "12px" }}>🕷️ Web Scraper (Admin)</h5>

      {stats && (
        <div className="row g-2 mb-3" style={{ fontSize: "0.9rem" }}>
          <div className="col-6">Total: <strong>{stats.db_total}</strong></div>
          <div className="col-6">Active: <strong>{stats.active}</strong></div>
          <div className="col-6">Auto-scraped: <strong>{stats.auto_scraped}</strong></div>
          <div className="col-6">
            Last run: <strong>
              {stats.last_run?.at ? new Date(stats.last_run.at).toLocaleString() : "Never"}
            </strong>
          </div>
        </div>
      )}

      <button className="btn-sn" onClick={trigger} disabled={running}>
        {running ? "Scraping..." : "▶ Run Scraper Now"}
      </button>

      {result && !result.error && (
        <div className="alert alert-success mt-3 mb-0" style={{ fontSize: "0.9rem" }}>
          ✅ Scraped <strong>{result.total_scraped}</strong>,
          saved <strong>{result.total_saved}</strong>,
          skipped <strong>{result.total_duplicates}</strong> duplicates,
          invalid <strong>{result.total_invalid}</strong>
        </div>
      )}

      {result?.error && (
        <div className="alert alert-danger mt-3 mb-0">{result.error}</div>
      )}
    </div>
  );
}