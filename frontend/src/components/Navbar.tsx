"use client";
import { useState } from "react";
import Link from "next/link";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50" style={{ background: "rgba(6,13,31,0.92)", backdropFilter: "blur(16px)", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 no-underline">
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#1D4ED8,#3B82F6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ color: "white", fontWeight: 800, fontSize: "0.95rem", fontFamily: "Space Grotesk, sans-serif" }}>IC</span>
          </div>
          <div>
            <span style={{ color: "white", fontWeight: 800, fontSize: "1.1rem", fontFamily: "Space Grotesk, sans-serif", letterSpacing: "-0.02em" }}>
              ICP3A
            </span>
            <span style={{ color: "#F59E0B", fontWeight: 800, fontSize: "1.1rem", fontFamily: "Space Grotesk, sans-serif" }}>.</span>
          </div>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-8">
          <Link href="/services" className="nav-link">Services</Link>
          <Link href="/pricing" className="nav-link">Pricing</Link>
          <Link href="/about" className="nav-link">About</Link>
          <Link href="/lpi" className="nav-link">LPI Certification</Link>
          <Link href="/contact" className="nav-link">Contact</Link>
        </div>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">
          <Link href="/dashboard" className="nav-link" style={{ color: "rgba(255,255,255,0.6)" }}>Dashboard</Link>
          <Link href="/contact" className="btn-gold" style={{ padding: "8px 20px", fontSize: "0.875rem" }}>
            Get Started
          </Link>
        </div>

        {/* Mobile burger */}
        <button className="md:hidden" onClick={() => setOpen(!open)} style={{ background: "none", border: "none", cursor: "pointer", color: "white", padding: 4 }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {open ? <path d="M18 6L6 18M6 6l12 12" /> : <><path d="M3 12h18" /><path d="M3 6h18" /><path d="M3 18h18" /></>}
          </svg>
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div style={{ background: "#060D1F", borderTop: "1px solid rgba(255,255,255,0.07)" }} className="md:hidden px-6 pb-6 pt-4 flex flex-col gap-4">
          {["Services", "Pricing", "About", "LPI Certification", "Contact"].map(item => (
            <Link key={item} href={`/${item.toLowerCase().replace(/ /g, "-")}`} className="nav-link text-base" onClick={() => setOpen(false)}>{item}</Link>
          ))}
          <Link href="/contact" className="btn-gold mt-2 justify-center" onClick={() => setOpen(false)}>Get Started</Link>
        </div>
      )}
    </nav>
  );
}
