import React from "react";
import { Link } from "react-router-dom";

const isAvailable = (value) => {
  if (value === null || value === undefined || value === "") return false;
  if (typeof value === "string" && /^(not provided|not specified|n\/?a|unknown|null|none|-)$/i.test(value.trim())) return false;
  return true;
};

const firstAvailable = (...values) => values.find(isAvailable);
const formatMoney = (value) => {
  if (!isAvailable(value)) return null;
  const numeric = Number(String(value).replace(/[₹,\s]/g, ""));
  if (Number.isFinite(numeric)) {
    if (numeric <= 0) return null;
    return `₹${numeric.toLocaleString("en-IN")}`;
  }
  return String(value);
};

export default function ScholarshipCard({ scholarship, onBookmark, showMatch }) {
  const s = scholarship || {};
  const amount = formatMoney(firstAvailable(s.scholarship_amount, s.amount, s.award_amount));
  const deadline = firstAvailable(s.application_deadline, s.deadline, s.last_date);
  const course = firstAvailable(s.course, s.eligible_course, s.courses);
  const state = firstAvailable(s.state, s.location, s.eligible_state);
  const minPercentage = firstAvailable(s.minimum_percentage, s.min_percentage, s.minimum_marks, s.min_marks);
  const familyIncome = firstAvailable(s.max_family_income, s.family_income_limit, s.income_limit, s.maximum_family_income);

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
          <h5 className="mb-1">{s.scholarship_name || s.title || "Scholarship"}</h5>
          {isAvailable(s.provider) && <p className="text-muted mb-1 small">{s.provider}</p>}
        </div>
        <div className="text-end">
          {showMatch && s.match_percentage !== undefined && (
            <span className={`match-badge ${matchClass()}`}>{s.match_percentage}% match</span>
          )}
        </div>
      </div>

      <div className="row small mt-2 g-2">
        {amount && <div className="col-md-6"><div className="p-2 bg-light rounded">💰 <strong>Amount</strong><br />{amount}</div></div>}
        {isAvailable(deadline) && <div className="col-md-6"><div className="p-2 bg-light rounded">📅 <strong>Deadline</strong><br />{deadline}</div></div>}
        {isAvailable(course) && <div className="col-md-6"><div className="p-2 bg-light rounded">📚 <strong>Course</strong><br />{Array.isArray(course) ? course.join(", ") : course}</div></div>}
        {isAvailable(state) && <div className="col-md-6"><div className="p-2 bg-light rounded">📍 <strong>State</strong><br />{Array.isArray(state) ? state.join(", ") : state}</div></div>}
        {isAvailable(minPercentage) && <div className="col-md-6 mt-2">Minimum Percentage: <strong>{minPercentage}{String(minPercentage).includes("%") ? "" : "%"}</strong></div>}
        {isAvailable(familyIncome) && <div className="col-md-6 mt-2">Family Income Limit: <strong>{formatMoney(familyIncome) || familyIncome}</strong></div>}
      </div>

      <div className="mt-3 d-flex gap-2">
        <Link to={`/scholarships/${s.scholarship_id || s.id}`} className="btn btn-primary btn-sm">View Details</Link>
        {onBookmark && (s.scholarship_id || s.id) && (
          <button className="btn btn-outline-warning btn-sm" onClick={() => onBookmark(s.scholarship_id || s.id)}>🔖 Bookmark</button>
        )}
      </div>
    </div>
  );
}
