import React, { useEffect, useState } from "react";
import { listScholarships, compareScholarships } from "../services/api";

export default function Compare() {
  const [all, setAll] = useState([]);
  const [selected, setSelected] = useState([]);
  const [items, setItems] = useState([]);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const res = await listScholarships();
    setAll(res.data.results || []);
  };

  const handleSelect = (id) => {
    setSelected((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  };

  const handleCompare = async () => {
    if (selected.length < 2) return alert("Select at least 2");
    const res = await compareScholarships(selected);
    setItems(res.data);
  };

  return (
    <div>
      <h3>⚖️ Compare Scholarships</h3>
      <div className="card p-3 mb-3">
        <p className="text-muted">Select 2 or more scholarships:</p>
        <div className="row">
          {all.map((s) => (
            <div key={s.scholarship_id} className="col-md-6 mb-2">
              <div className="form-check">
                <input className="form-check-input" type="checkbox"
                  checked={selected.includes(s.scholarship_id)}
                  onChange={() => handleSelect(s.scholarship_id)} id={s.scholarship_id} />
                <label className="form-check-label" htmlFor={s.scholarship_id}>{s.scholarship_name}</label>
              </div>
            </div>
          ))}
        </div>
        <button className="btn btn-primary mt-3" onClick={handleCompare}>Compare Selected</button>
      </div>
      {items.length > 0 && (
        <div className="table-responsive">
          <table className="table table-bordered bg-white">
            <thead>
              <tr>
                <th>Field</th>
                {items.map((s) => <th key={s.scholarship_id}>{s.scholarship_name}</th>)}
              </tr>
            </thead>
            <tbody>
              {["provider", "scholarship_amount", "application_deadline", "minimum_percentage", "max_family_income", "course", "state"].map((f) => (
                <tr key={f}>
                  <td><strong>{f.replace(/_/g, " ")}</strong></td>
                  {items.map((s) => <td key={s.scholarship_id}>{String(s[f])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}