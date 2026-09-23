import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getRecommendations, getBookmarks, getUpcomingDeadlines } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [recs, setRecs] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [deadlines, setDeadlines] = useState([]);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [r, b, d] = await Promise.all([
        getRecommendations().catch(() => ({ data: { recommendations: [] } })),
        getBookmarks().catch(() => ({ data: [] })),
        getUpcomingDeadlines().catch(() => ({ data: [] }))
      ]);
      setRecs(r.data.recommendations || []);
      setBookmarks(b.data || []);
      setDeadlines(d.data || []);
    } catch (e) {}
  };

  return (
    <div>
      <div className="mb-4">
        <h2>Welcome back, {user?.name} 👋</h2>
        <p className="text-muted">Here's your ScholarNexus overview</p>
      </div>
      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card p-3 text-center">
            <h3 className="text-primary">{recs.length}</h3>
            <p className="mb-0">Recommended</p>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card p-3 text-center">
            <h3 className="text-warning">{bookmarks.length}</h3>
            <p className="mb-0">Bookmarked</p>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card p-3 text-center">
            <h3 className="text-danger">{deadlines.length}</h3>
            <p className="mb-0">Upcoming Deadlines</p>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-6">
          <div className="card p-3">
            <h5>🎯 Top Recommendations</h5>
            {recs.length === 0 ? (
              <p className="text-muted">Complete your <Link to="/profile">profile</Link> to see recommendations.</p>
            ) : (
              <ul className="list-group list-group-flush">
                {recs.slice(0, 5).map((s) => (
                  <li key={s.scholarship_id} className="list-group-item d-flex justify-content-between">
                    <Link to={`/scholarships/${s.scholarship_id}`}>{s.scholarship_name}</Link>
                    <span className="badge bg-success">{s.match_percentage}%</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="col-md-6">
          <div className="card p-3">
            <h5>⏰ Upcoming Deadlines</h5>
            {deadlines.length === 0 ? (
              <p className="text-muted">Bookmark scholarships to see deadlines here.</p>
            ) : (
              <ul className="list-group list-group-flush">
                {deadlines.slice(0, 5).map((s) => (
                  <li key={s.scholarship_id} className="list-group-item d-flex justify-content-between">
                    <span>{s.scholarship_name}</span>
                    <span className={s.days_left <= 7 ? "deadline-red" : s.days_left <= 15 ? "deadline-orange" : "deadline-green"}>
                      {s.days_left} days
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}