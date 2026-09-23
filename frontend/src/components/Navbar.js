import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path) =>
    location.pathname === path ? "nav-link active fw-bold" : "nav-link";

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4">
      <div className="container">
        <Link className="navbar-brand" to={user ? "/dashboard" : "/login"}>
          <span className="brand-icon">🎓</span>ScholarNexus
        </Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navMenu">
          {user && (
            <ul className="navbar-nav me-auto">
              <li className="nav-item"><Link className={isActive("/dashboard")} to="/dashboard">Dashboard</Link></li>
              <li className="nav-item"><Link className={isActive("/scholarships")} to="/scholarships">Scholarships</Link></li>
              <li className="nav-item"><Link className={isActive("/recommendations")} to="/recommendations">For You</Link></li>
              <li className="nav-item"><Link className={isActive("/bookmarks")} to="/bookmarks">Bookmarks</Link></li>
              <li className="nav-item"><Link className={isActive("/deadlines")} to="/deadlines">Deadlines</Link></li>
              <li className="nav-item"><Link className={isActive("/compare")} to="/compare">Compare</Link></li>
            </ul>
          )}
          <ul className="navbar-nav ms-auto">
            {user ? (
              <>
                <li className="nav-item">
                  <span className="nav-link">👤 {user.name} <small className="text-muted">({user.role})</small></span>
                </li>
                <li className="nav-item">
                  <button className="btn btn-outline-danger btn-sm mt-1" onClick={handleLogout}>Logout</button>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item"><Link className={isActive("/login")} to="/login">Login</Link></li>
                <li className="nav-item"><Link className={isActive("/register")} to="/register">Register</Link></li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}