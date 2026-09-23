import React, { useEffect, useState } from "react";
import { getUpcomingDeadlines } from "../services/api";
import { Link } from "react-router-dom";

export default function Deadlines() {
  const [items, setItems] = useState([]);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const res = await getUpcomingDeadlines();
    setItems(res.data || []);
  };

  const urgency = (d) => d <= 7 ? "deadline-red" : d <= 15 ? "deadline-orange" : "deadline-green";

  return (
    <div>
      <h3>⏰ Upcoming Deadlines (next 30 days)</h3>
      {items.length === 0 ? (
        <p className="text-muted">No upcoming deadlines from your bookmarks.</p>
      ) : (
        items.map((s) => (
          <div key={s.scholarship_id} className="card p-3 mb-2 d-flex justify-content-between flex-row">
            <div>
              <Link to={`/scholarships/${s.scholarship_id}`}>{s.scholarship_name}</Link>
              <p className="text-muted small mb-0">{s.provider} • Due {s.application_deadline}</p>
            </div>
            <div className={urgency(s.days_left)}>{s.days_left} days left</div>
          </div>
        ))
      )}
    </div>
  );
}