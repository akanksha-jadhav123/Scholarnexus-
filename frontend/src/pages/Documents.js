import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getDocumentChecklist, updateDocument } from "../services/api";

export default function Documents() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => { load(); }, [id]);

  const load = async () => {
    const res = await getDocumentChecklist(id);
    setData(res.data);
  };

  const toggle = async (name, status) => {
    await updateDocument(id, {
      document_name: name,
      status: status === "completed" ? "pending" : "completed"
    });
    load();
  };

  if (!data) return <div className="text-center py-5">Loading...</div>;

  const pct = data.total > 0 ? Math.round((data.completed / data.total) * 100) : 0;

  return (
    <div className="animate-in">
      <Link to={`/scholarships/${id}`} className="btn-sn-ghost mb-3" style={{ textDecoration: "none" }}>
        ← Back
      </Link>

      <div className="sn-card mb-4">
        <h3 style={{ fontWeight: 800 }}>📄 Document Checklist</h3>
        <p style={{ color: "var(--gray)" }}>{data.scholarship_name}</p>
        <div className="d-flex justify-content-between mb-2" style={{ fontSize: "0.9rem" }}>
          <span>Progress</span>
          <strong>{data.completed} / {data.total} ({pct}%)</strong>
        </div>
        <div className="progress-sn">
          <div className="progress-sn-bar" style={{ width: `${pct}%` }}></div>
        </div>
      </div>

      {data.checklist.map((doc) => (
        <div className="sn-card mb-2 d-flex align-items-center gap-3" key={doc.document_name}>
          <input
            type="checkbox"
            checked={doc.status === "completed"}
            onChange={() => toggle(doc.document_name, doc.status)}
            style={{ width: "20px", height: "20px", cursor: "pointer" }}
          />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600 }}>{doc.document_name}</div>
            <div style={{ fontSize: "0.85rem", color: "var(--gray)" }}>
              {doc.status === "completed" ? "✅ Ready" : "⏳ Pending"}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}