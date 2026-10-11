import React, { useEffect, useState } from "react";
import {
  searchScholarships,
  toggleBookmark,
} from "../services/api";
import ScholarshipCard from "../components/ScholarshipCard";

const STATES = [
  "All",
  "Maharashtra",
  "Karnataka",
  "Tamil Nadu",
  "Gujarat",
  "Uttar Pradesh",
];

const CATEGORIES = [
  "All",
  "General",
  "OBC",
  "SC",
  "ST",
  "Minority",
];

const GENDERS = [
  "All",
  "Male",
  "Female",
  "Other",
];

const COURSES = [
  "All",
  "B.Tech",
  "B.Sc",
  "B.Com",
  "B.A",
];

export default function ScholarshipList() {
  const [filters, setFilters] = useState({
    q: "",
    state: "All",
    category: "All",
    gender: "All",
    course: "All",
    max_income: "",
    min_percentage: "",
    sort_by: "application_deadline",
    order: "asc",
  });

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    setLoading(true);
    setError("");

    try {
      const params = {};

      Object.entries(filters).forEach(([key, value]) => {
        if (value !== "" && value !== "All") {
          params[key] = value;
        }
      });

      const res = await searchScholarships(params);

      setResults(res.data?.results || []);
    } catch (error) {
      console.error("Scholarship loading error:", error);

      setError(
        error.response?.data?.error ||
          "Unable to load scholarships."
      );

      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const handleBookmark = async (id) => {
    try {
      const res = await toggleBookmark(id);

      alert(
        res.data?.message ||
          "Bookmark updated successfully!"
      );
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.error ||
          "Please login to bookmark scholarships."
      );
    }
  };

  const clearFilters = () => {
    setFilters({
      q: "",
      state: "All",
      category: "All",
      gender: "All",
      course: "All",
      max_income: "",
      min_percentage: "",
      sort_by: "application_deadline",
      order: "asc",
    });
  };

  return (
    <div className="container-fluid px-3 px-md-4 py-4">

      {/* HEADER */}

      <div className="mb-4">
        <h2 className="fw-bold mb-1">
          🎓 Scholarships
        </h2>

        <p className="text-muted mb-0">
          Discover scholarships matching your
          education and eligibility.
        </p>
      </div>

      {/* FILTERS */}

      <div className="sn-card mb-4">

        <h5 className="mb-3">
          🔍 Search & Filter
        </h5>

        <div className="row g-3">

          <div className="col-12 col-md-6 col-lg-3">
            <label className="form-label">
              Search
            </label>

            <input
              name="q"
              className="form-control"
              placeholder="Scholarship name/provider"
              value={filters.q}
              onChange={handleFilter}
            />
          </div>

          <div className="col-12 col-md-6 col-lg-2">
            <label className="form-label">
              State
            </label>

            <select
              name="state"
              className="form-select"
              value={filters.state}
              onChange={handleFilter}
            >
              {STATES.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
          </div>

          <div className="col-12 col-md-6 col-lg-2">
            <label className="form-label">
              Category
            </label>

            <select
              name="category"
              className="form-select"
              value={filters.category}
              onChange={handleFilter}
            >
              {CATEGORIES.map((category) => (
                <option
                  key={category}
                  value={category}
                >
                  {category}
                </option>
              ))}
            </select>
          </div>

          <div className="col-12 col-md-6 col-lg-2">
            <label className="form-label">
              Gender
            </label>

            <select
              name="gender"
              className="form-select"
              value={filters.gender}
              onChange={handleFilter}
            >
              {GENDERS.map((gender) => (
                <option key={gender} value={gender}>
                  {gender}
                </option>
              ))}
            </select>
          </div>

          <div className="col-12 col-md-6 col-lg-3">
            <label className="form-label">
              Course
            </label>

            <select
              name="course"
              className="form-select"
              value={filters.course}
              onChange={handleFilter}
            >
              {COURSES.map((course) => (
                <option key={course} value={course}>
                  {course}
                </option>
              ))}
            </select>
          </div>

          <div className="col-12 col-md-6 col-lg-3">
            <label className="form-label">
              Maximum Family Income
            </label>

            <input
              type="number"
              name="max_income"
              className="form-control"
              placeholder="e.g. 500000"
              value={filters.max_income}
              onChange={handleFilter}
            />
          </div>

          <div className="col-12 col-md-6 col-lg-3">
            <label className="form-label">
              Minimum Percentage
            </label>

            <input
              type="number"
              name="min_percentage"
              className="form-control"
              placeholder="e.g. 75"
              value={filters.min_percentage}
              onChange={handleFilter}
            />
          </div>

          <div className="col-12 col-md-6 col-lg-3">
            <label className="form-label">
              Sort By
            </label>

            <select
              name="sort_by"
              className="form-select"
              value={filters.sort_by}
              onChange={handleFilter}
            >
              <option value="application_deadline">
                Deadline
              </option>

              <option value="scholarship_amount">
                Amount
              </option>

              <option value="minimum_percentage">
                Minimum Percentage
              </option>
            </select>
          </div>

          <div className="col-12 col-md-6 col-lg-3 d-flex align-items-end gap-2">

            <button
              className="btn btn-primary flex-grow-1"
              onClick={fetchResults}
            >
              Apply Filters
            </button>

            <button
              className="btn btn-outline-secondary"
              onClick={clearFilters}
            >
              Clear
            </button>

          </div>

        </div>
      </div>

      {/* RESULTS HEADER */}

      <div className="d-flex justify-content-between align-items-center mb-3">

        <div>
          <strong>
            {results.length}
          </strong>{" "}
          scholarships found
        </div>

      </div>

      {/* ERROR */}

      {error && (
        <div className="alert alert-danger">
          ⚠️ {error}
        </div>
      )}

      {/* LOADING */}

      {loading ? (
        <div className="sn-card text-center py-5">

          <div className="spinner-border text-primary mb-3" />

          <p className="text-muted mb-0">
            Loading scholarships...
          </p>

        </div>
      ) : results.length === 0 ? (

        <div className="sn-card text-center py-5">

          <div style={{ fontSize: "3rem" }}>
            🎓
          </div>

          <h5 className="mt-3">
            No scholarships found
          </h5>

          <p className="text-muted">
            Try changing your filters.
          </p>

        </div>

      ) : (

        <div className="row g-3">

          {results.map((scholarship) => (

            <div
              className="col-12 col-lg-6"
              key={scholarship.scholarship_id}
            >

              <ScholarshipCard
                scholarship={scholarship}
                onBookmark={handleBookmark}
              />

            </div>

          ))}

        </div>

      )}

    </div>
  );
}