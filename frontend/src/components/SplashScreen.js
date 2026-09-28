import React from "react";
import { LogoFull } from "./Logo";

export default function SplashScreen() {
  return (
    <div className="sn-splash">
      <div className="sn-splash-pulse">
        <LogoFull size={64} color="var(--dark)" />
      </div>
      <p style={{ color: "var(--gray)", fontSize: "0.9rem" }}>Loading...</p>
    </div>
  );
}