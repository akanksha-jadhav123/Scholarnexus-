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

  const isAdmin = user?.role === "admin";

  return (
    <nav className="sn-navbar">
      <div className="container-fluid px-4 d-flex align-items-center">
        {/* LOGO — links to correct home based on role */}
        <Link
          className="navbar-brand me-4"
          to={isAdmin ? "/admin" : user ? "/dashboard" : "/"}
          style={{ textDecoration: "none", flexShrink: 0 }}
        >
          <LogoFull size={34} color="var(--dark)" />
        </Link>

        {/* NAV LINKS — change based on role */}
        <div className="d-none d-lg-flex align-items-center" style={{ gap: "2px" }}>
          {user ? (
            isAdmin ? (
              // ==================== ADMIN NAV ====================
              <>
                <Link className={isActive("/admin")} to="/admin">
                  Dashboard
                </Link>
                <Link className={isActive("/admin/scholarships")} to="/admin/scholarships">
                  Scholarships
                </Link>
                <Link className={isActive("/admin/sources")} to="/admin/sources">
                  Sources
                </Link>
                <Link className={isActive("/admin/users")} to="/admin/users">
                  Users
                </Link>
                <Link className={isActive("/scholarships")} to="/scholarships">
                  Browse
                </Link>
              </>
            ) : (
              // ==================== STUDENT NAV ====================
              <>
                <Link className={isActive("/dashboard")} to="/dashboard">Dashboard</Link>
                <Link className={isActive("/scholarships")} to="/scholarships">Scholarships</Link>
                <Link className={isActive("/recommendations")} to="/recommendations">For You</Link>
                <Link className={isActive("/bookmarks")} to="/bookmarks">Bookmarks</Link>
                <Link className={isActive("/deadlines")} to="/deadlines">Deadlines</Link>
                <Link className={isActive("/compare")} to="/compare">Compare</Link>
                <Link className={isActive("/applications")} to="/applications">Applications</Link>
              </>
            )
          ) : (
            // ==================== GUEST NAV ====================
            <>
              <Link className={isActive("/")} to="/">Home</Link>
              <Link className={isActive("/scholarships")} to="/scholarships">Scholarships</Link>
            </>
          )}
        </div>

        {/* USER AREA */}
        <div className="ms-auto d-flex align-items-center" style={{ gap: "10px" }}>
          {user ? (
            <>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "6px 14px",
                  background: isAdmin ? "#fef2f2" : "var(--light)",
                  borderRadius: "999px",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  whiteSpace: "nowrap",
                  border: isAdmin ? "1px solid #fecaca" : "none"
                }}
              >
                <div
                  style={{
                    width: "26px",
                    height: "26px",
                    borderRadius: "50%",
                    background: isAdmin
                      ? "linear-gradient(135deg, #dc3545, #b91c1c)"
                      : "linear-gradient(135deg, var(--primary), var(--secondary))",
                    color: "white",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "0.75rem",
                    fontWeight: 700
                  }}
                >
                  {user.name?.charAt(0).toUpperCase()}
                </div>
                <span>{user.name?.split(" ")[0]}</span>
                {isAdmin && (
                  <span
                    style={{
                      background: "#dc3545",
                      color: "white",
                      fontSize: "0.6rem",
                      padding: "2px 7px",
                      borderRadius: "999px",
                      fontWeight: 800,
                      letterSpacing: "0.5px"
                    }}
                  >
                    ADMIN
                  </span>
                )}
              </div>

              <button
                className="btn-sn-ghost"
                onClick={handleLogout}
                style={{ whiteSpace: "nowrap" }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="btn-sn-ghost"
                style={{ textDecoration: "none", whiteSpace: "nowrap" }}
              >
                Login
              </Link>
              <Link
                to="/register"
                className="btn-sn"
                style={{ textDecoration: "none", whiteSpace: "nowrap" }}
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}