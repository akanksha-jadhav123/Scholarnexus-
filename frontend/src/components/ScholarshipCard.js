import React from "react";
import { Link } from "react-router-dom";

export default function ScholarshipCard({ scholarship, onBookmark, showMatch }) {
  const s = scholarship;

  const matchClass = () => {
    if (!s.match_percentage) return "";
    if (s.match_percentage >= 70) return "match-high";
    if (s.match_percentage >= 40) return "match-mid";
    return "match-low";
  };

  return (
    <div className="card mb-3 p-3">
      <div className="d-flex justify-content-between align-items-start">
        <div>
          <h5 className="mb-1">{s.scholarship_name}</h5>
          <p className="text-muted mb-1 small">{s.provider}</p>
        </div>
        <div className="text-end">
          {showMatch && s.match_percentage !== undefined && (
            <span className={`match-badge ${matchClass()}`}>{s.match_percentage}% match</span>
          )}
        </div>
      </div>
      <div className="row small mt-2">
        <div className="col-md-3">💰 ₹{s.scholarship_amount}</div>
        <div className="col-md-3">📚 {s.course}</div>
        <div className="col-md-3">📍 {s.state}</div>
        <div className="col-md-3">📅 {s.application_deadline}</div>
      </div>
      <div className="mt-3 d-flex gap-2">
        <Link to={`/scholarships/${s.scholarship_id}`} className="btn btn-primary btn-sm">View Details</Link>
        {onBookmark && (
          <button className="btn btn-outline-warning btn-sm" onClick={() => onBookmark(s.scholarship_id)}>🔖 Bookmark</button>
        )}
      </div>
    </div>
  );
}