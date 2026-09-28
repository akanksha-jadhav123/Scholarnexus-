import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogoFull } from "./Logo";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const isActive = (path) =>
    location.pathname === path ? "nav-link active" : "nav-link";

  return (
    <nav className="sn-navbar">
      <div className="container d-flex align-items-center">
        <Link className="navbar-brand me-4" to={user ? "/dashboard" : "/"} style={{ textDecoration: "none" }}>
          <LogoFull size={38} color="var(--dark)" />
        </Link>

        <div className="d-none d-lg-flex flex-grow-1">
          {user ? (
            <>
              <Link className={isActive("/dashboard")} to="/dashboard">Dashboard</Link>
              <Link className={isActive("/scholarships")} to="/scholarships">Scholarships</Link>
              <Link className={isActive("/recommendations")} to="/recommendations">For You</Link>
              <Link className={isActive("/bookmarks")} to="/bookmarks">Bookmarks</Link>
              <Link className={isActive("/deadlines")} to="/deadlines">Deadlines</Link>
              <Link className={isActive("/compare")} to="/compare">Compare</Link>
            </>
          ) : (
            <>
              <Link className={isActive("/")} to="/">Home</Link>
              <Link className={isActive("/scholarships")} to="/scholarships">Scholarships</Link>
            </>
          )}
        </div>

        <div className="ms-auto d-flex align-items-center gap-2">
          {user ? (
            <>
              <div style={{
                display: "flex", alignItems: "center", gap: "8px",
                padding: "6px 12px", background: "var(--light)",
                borderRadius: "999px", fontSize: "0.85rem", fontWeight: 600
              }}>
                <div style={{
                  width: "28px", height: "28px", borderRadius: "50%",
                  background: "linear-gradient(135deg, var(--primary), var(--secondary))",
                  color: "white", display: "flex", alignItems: "center",
                  justifyContent: "center", fontSize: "0.8rem", fontWeight: 700
                }}>
                  {user.name?.charAt(0).toUpperCase()}
                </div>
                <span className="d-none d-md-inline">{user.name?.split(" ")[0]}</span>
              </div>
              <button className="btn-sn-ghost" onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-sn-ghost" style={{ textDecoration: "none" }}>Login</Link>
              <Link to="/register" className="btn-sn" style={{ textDecoration: "none" }}>Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}