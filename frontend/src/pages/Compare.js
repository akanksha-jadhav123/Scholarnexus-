import React, { useEffect, useState } from "react";
import {
  listScholarships,
  compareScholarships,
} from "../services/api";

export default function Compare() {
  const [all, setAll] = useState([]);
  const [selected, setSelected] = useState([]);
  const [comparison, setComparison] = useState(null);

  const [loading, setLoading] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [error, setError] = useState("");

  // =====================================================
  // LOAD SCHOLARSHIPS
  // =====================================================

  useEffect(() => {
    loadScholarships();
  }, []);

  const loadScholarships = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await listScholarships();

      const scholarships = res.data?.results || [];

      setAll(scholarships);
    } catch (err) {
      console.error("Failed to load scholarships:", err);

      setError(
        err.response?.data?.error ||
          "Unable to load scholarships. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // SELECT / UNSELECT SCHOLARSHIP
  // =====================================================

  const handleSelect = (id) => {
    setError("");

    setSelected((prev) => {
      // Remove
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }

      // Maximum 5
      if (prev.length >= 5) {
        setError("You can compare a maximum of 5 scholarships.");
        return prev;
      }

      return [...prev, id];
    });

    // Clear previous comparison when selection changes
    setComparison(null);
  };

  // =====================================================
  // COMPARE
  // =====================================================

  const handleCompare = async () => {
    setError("");

    if (selected.length < 2) {
      setError("Please select at least 2 scholarships.");
      return;
    }

    if (selected.length > 5) {
      setError("You can compare a maximum of 5 scholarships.");
      return;
    }

    setCompareLoading(true);

    try {
      const res = await compareScholarships(selected);

      console.log("Comparison API response:", res.data);

      // Backend returns:
      //
      // {
      //   count: 2,
      //   scholarships: [...],
      //   rows: [...]
      // }

      if (!res.data || !Array.isArray(res.data.rows)) {
        throw new Error(
          "Invalid comparison response received from server."
        );
      }

      setComparison(res.data);

      // Scroll to comparison result
      setTimeout(() => {
        document
          .getElementById("comparison-result")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 100);
    } catch (err) {
      console.error("Comparison failed:", err);

      setError(
        err.response?.data?.error ||
          err.message ||
          "Unable to compare scholarships."
      );

      setComparison(null);
    } finally {
      setCompareLoading(false);
    }
  };

  // =====================================================
  // CLEAR SELECTION
  // =====================================================

  const clearComparison = () => {
    setSelected([]);
    setComparison(null);
    setError("");
  };

  // =====================================================
  // FORMAT VALUES
  // =====================================================

  const formatValue = (value, field) => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      value === "None"
    ) {
      return "—";
    }

    if (field === "scholarship_amount") {
      const number = Number(value);

      if (!Number.isNaN(number)) {
        return `₹${number.toLocaleString("en-IN")}`;
      }
    }

    if (field === "max_family_income") {
      const number = Number(value);

      if (!Number.isNaN(number)) {
        return `₹${number.toLocaleString("en-IN")}`;
      }
    }

    if (field === "minimum_percentage") {
      return `${value}%`;
    }

    if (field === "application_deadline") {
      try {
        const date = new Date(value);

        if (!Number.isNaN(date.getTime())) {
          return date.toLocaleDateString("en-IN", {
            day: "2-digit",
            month: "short",
            year: "numeric",
          });
        }
      } catch (e) {
        // Keep original value
      }
    }

    return String(value);
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="container py-4">
        <div className="sn-card text-center">
          <div className="spinner-border text-primary mb-3" />
          <h5>Loading scholarships...</h5>
          <p className="text-muted mb-0">
            Please wait while we load available scholarships.
          </p>
        </div>
      </div>
    );
  }

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="container-fluid px-3 px-md-4 py-4">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
        <div>
          <h3 className="mb-1">
            ⚖️ Compare Scholarships
          </h3>

          <p className="text-muted mb-0">
            Select 2 to 5 scholarships and compare them side-by-side.
          </p>
        </div>

        {selected.length > 0 && (
          <div>
            <span className="badge bg-primary fs-6 me-2">
              {selected.length} Selected
            </span>

            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={clearComparison}
            >
              Clear
            </button>
          </div>
        )}
      </div>

      {/* =================================================
          ERROR
      ================================================= */}

      {error && (
        <div
          className="alert alert-danger d-flex justify-content-between align-items-center"
          role="alert"
        >
          <span>⚠️ {error}</span>

          <button
            className="btn-close"
            onClick={() => setError("")}
          />
        </div>
      )}

      {/* =================================================
          SELECTION CARD
      ================================================= */}

      <div className="sn-card mb-4">

        <div className="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h5 className="mb-1">
              Select Scholarships
            </h5>

            <small className="text-muted">
              Choose at least 2 and maximum 5 scholarships.
            </small>
          </div>

          <span
            className={
              selected.length >= 2
                ? "badge bg-success"
                : "badge bg-secondary"
            }
          >
            {selected.length}/5
          </span>
        </div>

        {/* =================================================
            SCHOLARSHIP LIST
        ================================================= */}

        {all.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-muted">
              No active scholarships found.
            </p>

            <button
              className="btn btn-primary"
              onClick={loadScholarships}
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="row g-3">

            {all.map((scholarship) => {
              const id = scholarship.scholarship_id;

              const isSelected = selected.includes(id);

              return (
                <div
                  key={id}
                  className="col-12 col-md-6 col-lg-4"
                >
                  <div
                    className={`compare-selection-card ${
                      isSelected
                        ? "compare-selection-card-selected"
                        : ""
                    }`}
                    onClick={() => handleSelect(id)}
                  >

                    <div className="form-check">

                      <input
                        className="form-check-input"
                        type="checkbox"
                        id={`compare-${id}`}
                        checked={isSelected}
                        onChange={() =>
                          handleSelect(id)
                        }
                        onClick={(e) =>
                          e.stopPropagation()
                        }
                      />

                      <label
                        className="form-check-label"
                        htmlFor={`compare-${id}`}
                      >
                        <strong>
                          {scholarship.scholarship_name ||
                            "Unnamed Scholarship"}
                        </strong>
                      </label>

                    </div>

                    <div className="compare-card-info">

                      <div>
                        <span className="text-muted">
                          Provider
                        </span>

                        <strong>
                          {scholarship.provider || "—"}
                        </strong>
                      </div>

                      <div>
                        <span className="text-muted">
                          Amount
                        </span>

                        <strong>
                          {formatValue(
                            scholarship.scholarship_amount,
                            "scholarship_amount"
                          )}
                        </strong>
                      </div>

                      <div>
                        <span className="text-muted">
                          Deadline
                        </span>

                        <strong>
                          {formatValue(
                            scholarship.application_deadline,
                            "application_deadline"
                          )}
                        </strong>
                      </div>

                    </div>

                  </div>
                </div>
              );
            })}

          </div>
        )}

        {/* =================================================
            COMPARE BUTTON
        ================================================= */}

        <div className="mt-4">

          <button
            className="btn btn-primary w-100"
            onClick={handleCompare}
            disabled={
              selected.length < 2 ||
              compareLoading
            }
          >

            {compareLoading ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                />

                Comparing...
              </>
            ) : (
              <>
                ⚖️ Compare {selected.length} Selected
              </>
            )}

          </button>

          {selected.length < 2 && (
            <small className="text-muted d-block text-center mt-2">
              Select at least 2 scholarships to compare.
            </small>
          )}

        </div>

      </div>

      {/* =================================================
          COMPARISON RESULT
      ================================================= */}

      {comparison && (
        <div
          id="comparison-result"
          className="sn-card mb-5"
        >

          <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">

            <div>
              <h4 className="mb-1">
                📊 Comparison Result
              </h4>

              <p className="text-muted mb-0">
                Comparing{" "}
                <strong>
                  {comparison.count}
                </strong>{" "}
                scholarships.
              </p>
            </div>

            <button
              className="btn btn-outline-primary btn-sm"
              onClick={() =>
                document
                  .getElementById("comparison-result")
                  ?.scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              View Comparison
            </button>

          </div>

          {/* =================================================
              COMPARISON TABLE
          ================================================= */}

          <div className="table-responsive">

            <table className="table table-bordered table-hover align-middle comparison-table">

              <thead className="table-light">

                <tr>

                  <th
                    style={{
                      minWidth: "190px",
                      position: "sticky",
                      left: 0,
                      zIndex: 2,
                      background: "#f8f9fa",
                    }}
                  >
                    Feature
                  </th>

                  {comparison.scholarships.map(
                    (scholarship) => (
                      <th
                        key={scholarship.scholarship_id}
                        style={{
                          minWidth: "240px",
                        }}
                      >
                        <div className="fw-bold">
                          {scholarship.scholarship_name}
                        </div>

                        <small className="text-muted">
                          {scholarship.scholarship_id}
                        </small>
                      </th>
                    )
                  )}

                </tr>

              </thead>

              <tbody>

                {comparison.rows.map((row) => (

                  <tr key={row.field}>

                    <th
                      style={{
                        position: "sticky",
                        left: 0,
                        background: "white",
                        zIndex: 1,
                      }}
                    >
                      {row.label}
                    </th>

                    {row.values.map(
                      (value, index) => {

                        const isBest =
                          row.best === index;

                        return (
                          <td
                            key={`${row.field}-${index}`}
                            className={
                              isBest
                                ? "comparison-best"
                                : ""
                            }
                          >

                            <div className="d-flex justify-content-between align-items-center gap-2">

                              <span>
                                {formatValue(
                                  value,
                                  row.field
                                )}
                              </span>

                              {isBest && (
                                <span
                                  className="badge bg-success"
                                  title="Best value"
                                >
                                  ✓ Best
                                </span>
                              )}

                            </div>

                          </td>
                        );
                      }
                    )}

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

          {/* =================================================
              LEGEND
          ================================================= */}

          <div className="mt-3">

            <small className="text-muted">
              <span className="badge bg-success me-2">
                ✓ Best
              </span>

              The highlighted value is considered better
              according to the comparison rules.
            </small>

          </div>

        </div>
      )}

    </div>
  );
}