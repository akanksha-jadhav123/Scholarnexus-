import React, { useState, useEffect } from "react";
import { createScholarship, updateScholarship } from "../services/api";

const EMPTY_FORM = {
  scholarship_id: "",
  scholarship_name: "",
  provider: "",
  application_deadline: "",
  scholarship_amount: "",
  minimum_percentage: "",
  max_family_income: "",
  state: "All",
  category: "All",
  gender: "All",
  course: "All",
  application_url: "",
  official_source: "",
  eligibility_description: "",
  required_documents: "",
  status: "Active",
};

const STATES = [
  "All", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat",
  "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "West Bengal",
  "Telangana", "Andhra Pradesh", "Kerala", "Delhi", "Bihar",
  "Odisha", "Punjab", "Haryana", "Goa", "Jharkhand",
  "Chhattisgarh", "Assam", "International",
];

const CATEGORIES = [
  "All", "General", "OBC", "SC", "ST", "Minority", "EBC", "EWS", "VJNT", "SBC",
];

const GENDERS = ["All", "Male", "Female", "Other"];

const COURSES = [
  "All", "B.Tech", "B.E.", "B.Sc", "B.Com", "B.A.", "BBA", "BCA",
  "M.Tech", "MBA", "M.Sc", "M.Com", "PhD", "Diploma", "ITI",
];

export default function ManualScholarshipForm({ onSuccess, onCancel, editData = null }) {
  const isEdit = Boolean(editData);

  const [form, setForm] = useState(() => {
    if (isEdit) {
      return {
        ...EMPTY_FORM,
        ...editData,
        required_documents: Array.isArray(editData.required_documents)
          ? editData.required_documents.join(", ")
          : editData.required_documents || "",
      };
    }
    return EMPTY_FORM;
  });

  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isEdit) {
      setForm({
        ...EMPTY_FORM,
        ...editData,
        required_documents: Array.isArray(editData.required_documents)
          ? editData.required_documents.join(", ")
          : editData.required_documents || "",
      });
    } else {
      setForm(EMPTY_FORM);
    }
  }, [editData, isEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  // ---------- CLIENT-SIDE VALIDATION ----------
  const validate = () => {
    const errs = {};

    if (!form.scholarship_id.trim()) {
      errs.scholarship_id = "Required";
    } else if (!/^[A-Za-z0-9_-]+$/.test(form.scholarship_id.trim())) {
      errs.scholarship_id = "Only letters, numbers, - and _";
    }

    if (!form.scholarship_name.trim()) errs.scholarship_name = "Required";
    if (!form.provider.trim()) errs.provider = "Required";
    if (!form.application_deadline) errs.application_deadline = "Required";

    if (form.application_deadline) {
      const d = new Date(form.application_deadline);
      if (isNaN(d.getTime())) errs.application_deadline = "Invalid date";
    }

    const num = (v) => (v === "" || v == null ? null : Number(v));
    const pct = num(form.minimum_percentage);
    if (pct != null && (pct < 0 || pct > 100)) {
      errs.minimum_percentage = "Must be 0–100";
    }

    const income = num(form.max_family_income);
    if (income != null && income < 0) {
      errs.max_family_income = "Must be positive";
    }

    const amount = num(form.scholarship_amount);
    if (amount != null && amount < 0) {
      errs.scholarship_amount = "Must be positive";
    }

    if (form.application_url && !/^https?:\/\//i.test(form.application_url)) {
      errs.application_url = "Must start with http:// or https://";
    }

    if (form.official_source && !/^https?:\/\//i.test(form.official_source)) {
      errs.official_source = "Must start with http:// or https://";
    }

    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // ---------- SUBMIT ----------
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validate()) {
      setError("Please fix the highlighted fields");
      return;
    }

    setSaving(true);

    // Build payload — strip empty strings so backend treats them as null
    const payload = { ...form };

    ["scholarship_amount", "minimum_percentage", "max_family_income"].forEach((k) => {
      if (payload[k] === "" || payload[k] == null) {
        delete payload[k];
      } else {
        payload[k] = Number(payload[k]);
      }
    });

    if (payload.required_documents) {
      payload.required_documents = payload.required_documents
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    } else {
      delete payload.required_documents;
    }

    try {
      if (isEdit) {
        await updateScholarship(editData.scholarship_id, payload);
      } else {
        await createScholarship(payload);
      }
      onSuccess?.();
      setForm(EMPTY_FORM);
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.message ||
        err.message ||
        "Save failed";
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  // ---------- RESET ----------
  const handleReset = () => {
    if (isEdit) {
      setForm({
        ...EMPTY_FORM,
        ...editData,
        required_documents: Array.isArray(editData.required_documents)
          ? editData.required_documents.join(", ")
          : editData.required_documents || "",
      });
    } else {
      setForm(EMPTY_FORM);
    }
    setError("");
    setFieldErrors({});
  };

  // ---------- RENDER HELPERS ----------
  const field = (name, label, props = {}) => (
    <div className={props.colClass || "col-md-6"}>
      <label className="form-label">
        {label} {props.required && <span style={{ color: "#dc3545" }}>*</span>}
      </label>
      <input
        className={`form-control ${fieldErrors[name] ? "is-invalid" : ""}`}
        name={name}
        value={form[name]}
        onChange={handleChange}
        {...props.input || {}}
      />
      {fieldErrors[name] && (
        <div className="invalid-feedback d-block">{fieldErrors[name]}</div>
      )}
      {props.help && !fieldErrors[name] && (
        <small className="text-muted">{props.help}</small>
      )}
    </div>
  );

  return (
    <div className="sn-card mb-3">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 style={{ fontWeight: 700, margin: 0 }}>
          {isEdit ? "✏️ Edit Scholarship" : "➕ Add Scholarship (Manual Entry)"}
        </h5>
        {onCancel && (
          <button type="button" className="btn-sn-ghost" onClick={onCancel}>
            ✕ Close
          </button>
        )}
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        {/* ---------- SECTION: IDENTITY ---------- */}
        <h6 style={{ fontWeight: 700, marginTop: "8px", marginBottom: "12px", color: "#4f46e5" }}>
          🆔 Identity
        </h6>
        <div className="row g-3">
          {field("scholarship_id", "Scholarship ID", {
            required: true,
            colClass: "col-md-4",
            input: {
              placeholder: "MANUAL001",
              disabled: isEdit,
              autoComplete: "off",
            },
            help: isEdit ? "Cannot be changed after creation" : "Unique identifier — letters, numbers, - and _",
          })}
          {field("scholarship_name", "Scholarship Name", {
            required: true,
            colClass: "col-md-8",
            input: {
              placeholder: "State Merit Scholarship 2026",
              autoComplete: "off",
            },
          })}
          {field("provider", "Provider / Issuing Body", {
            required: true,
            colClass: "col-md-6",
            input: { placeholder: "Government of Maharashtra" },
          })}
          {field("application_deadline", "Application Deadline", {
            required: true,
            colClass: "col-md-3",
            input: { type: "date" },
          })}
          <div className="col-md-3">
            <label className="form-label">Status</label>
            <select
              className="form-select"
              name="status"
              value={form.status}
              onChange={handleChange}
            >
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Expired">Expired</option>
            </select>
          </div>
        </div>

        {/* ---------- SECTION: FINANCIALS ---------- */}
        <h6 style={{ fontWeight: 700, marginTop: "22px", marginBottom: "12px", color: "#4f46e5" }}>
          💰 Financials
        </h6>
        <div className="row g-3">
          {field("scholarship_amount", "Scholarship Amount (₹)", {
            colClass: "col-md-4",
            input: { type: "number", min: 0, placeholder: "50000" },
            help: "Leave blank if not fixed",
          })}
          {field("min_family_income", "Minimum Family Income (₹)", {
            colClass: "col-md-4",
            input: { type: "number", min: 0, placeholder: "Optional" },
          })}
          {field("max_family_income", "Maximum Family Income (₹)", {
            colClass: "col-md-4",
            input: { type: "number", min: 0, placeholder: "800000" },
            help: "Leave blank if no limit",
          })}
        </div>

        {/* ---------- SECTION: ELIGIBILITY ---------- */}
        <h6 style={{ fontWeight: 700, marginTop: "22px", marginBottom: "12px", color: "#4f46e5" }}>
          🎯 Eligibility
        </h6>
        <div className="row g-3">
          {field("minimum_percentage", "Minimum Percentage", {
            colClass: "col-md-3",
            input: { type: "number", min: 0, max: 100, step: "0.01", placeholder: "75" },
          })}
          <div className="col-md-3">
            <label className="form-label">State</label>
            <select className="form-select" name="state" value={form.state} onChange={handleChange}>
              {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="col-md-3">
            <label className="form-label">Category</label>
            <select className="form-select" name="category" value={form.category} onChange={handleChange}>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="col-md-3">
            <label className="form-label">Gender</label>
            <select className="form-select" name="gender" value={form.gender} onChange={handleChange}>
              {GENDERS.map((g) => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>
          <div className="col-md-4">
            <label className="form-label">Course</label>
            <select className="form-select" name="course" value={form.course} onChange={handleChange}>
              {COURSES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="col-md-8">
            <label className="form-label">Eligibility Description</label>
            <textarea
              className="form-control"
              name="eligibility_description"
              value={form.eligibility_description}
              onChange={handleChange}
              rows={2}
              placeholder="Maharashtra domicile OBC students with 75%+ marks, family income under ₹8 lakh"
            />
          </div>
        </div>

        {/* ---------- SECTION: LINKS ---------- */}
        <h6 style={{ fontWeight: 700, marginTop: "22px", marginBottom: "12px", color: "#4f46e5" }}>
          🔗 Links
        </h6>
        <div className="row g-3">
          {field("application_url", "Application URL", {
            colClass: "col-md-6",
            input: { type: "url", placeholder: "https://mahadbt.maharashtra.gov.in/" },
            help: "Where the student applies",
          })}
          {field("official_source", "Official Source URL", {
            colClass: "col-md-6",
            input: { type: "url", placeholder: "https://..." },
            help: "Where the info came from (optional)",
          })}
        </div>

        {/* ---------- SECTION: DOCUMENTS ---------- */}
        <h6 style={{ fontWeight: 700, marginTop: "22px", marginBottom: "12px", color: "#4f46e5" }}>
          📄 Documents
        </h6>
        <div className="row g-3">
          <div className="col-12">
            <label className="form-label">Required Documents</label>
            <input
              className="form-control"
              name="required_documents"
              value={form.required_documents}
              onChange={handleChange}
              placeholder="Aadhaar Card, Income Certificate, Marksheet, Bank Passbook"
            />
            <small className="text-muted">
              Separate each document with a comma
            </small>
          </div>
        </div>

        {/* ---------- ACTIONS ---------- */}
        <div className="mt-4 d-flex gap-2 flex-wrap">
          <button type="submit" className="btn-sn" disabled={saving}>
            {saving ? "⏳ Saving..." : isEdit ? "💾 Update Scholarship" : "💾 Save Scholarship"}
          </button>
          <button type="button" className="btn-sn-ghost" onClick={handleReset} disabled={saving}>
            ↺ Reset
          </button>
          {onCancel && (
            <button type="button" className="btn-sn-ghost" onClick={onCancel} disabled={saving}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
}