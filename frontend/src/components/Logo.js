import React from "react";

// Full logo: icon + "ScholarNexus" text
export function LogoFull({ size = 36, color = "currentColor", showText = true }) {
  const iconSize = size;
  const textSize = size * 0.62;

  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: size * 0.25 }}>
      <LogoIcon size={iconSize} />
      {showText && (
        <span
          style={{
            fontSize: textSize,
            fontWeight: 800,
            letterSpacing: "-0.5px",
            color: color,
            lineHeight: 1,
          }}
        >
          Scholar<span style={{ color: "#0ea5e9" }}>Nexus</span>
        </span>
      )}
    </div>
  );
}

// Icon only: graduation cap + nexus network
export function LogoIcon({ size = 36 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ flexShrink: 0 }}
    >
      <defs>
        <linearGradient id="snGrad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#4f46e5" />
          <stop offset="50%" stopColor="#7c3aed" />
          <stop offset="100%" stopColor="#0ea5e9" />
        </linearGradient>
        <linearGradient id="snGradLight" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#a5b4fc" />
          <stop offset="100%" stopColor="#7dd3fc" />
        </linearGradient>
      </defs>

      {/* Rounded background */}
      <rect width="64" height="64" rx="16" fill="url(#snGrad)" />

      {/* Graduation cap */}
      <path
        d="M32 18L14 26L32 34L50 26L32 18Z"
        fill="white"
        fillOpacity="0.95"
      />

      {/* Cap base */}
      <path
        d="M22 29.5V36C22 36 26 40 32 40C38 40 42 36 42 36V29.5L32 34L22 29.5Z"
        fill="url(#snGradLight)"
      />

      {/* Tassel */}
      <path
        d="M50 26V33"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx="50" cy="34.5" r="2.5" fill="white" />

      {/* Nexus network dots (3 nodes) */}
      <circle cx="20" cy="46" r="3" fill="white" />
      <circle cx="32" cy="50" r="3" fill="white" />
      <circle cx="44" cy="46" r="3" fill="white" />

      {/* Network lines */}
      <path
        d="M20 46L32 50L44 46"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.8"
      />
    </svg>
  );
}

// Compact mark (just the cap, no background) — for favicons / small spaces
export function LogoMark({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="snMarkGrad" x1="0" y1="0" x2="64" y2="64">
          <stop offset="0%" stopColor="#4f46e5" />
          <stop offset="100%" stopColor="#0ea5e9" />
        </linearGradient>
      </defs>
      <path d="M32 12L8 22L32 32L56 22L32 12Z" fill="url(#snMarkGrad)" />
      <path d="M18 26V36C18 36 24 42 32 42C40 42 46 36 46 36V26L32 32L18 26Z" fill="url(#snMarkGrad)" fillOpacity="0.7" />
      <circle cx="56" cy="28" r="3" fill="url(#snMarkGrad)" />
    </svg>
  );
}

export default LogoFull;