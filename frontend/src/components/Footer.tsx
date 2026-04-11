"use client";
import Link from "next/link";

const cols = [
  {
    title: "Platform",
    links: ["LPI Certification", "Property Acquisition", "Agent Network", "Airport Zone Mapping", "AI Lead Scoring", "Document Verification"],
  },
  {
    title: "Company",
    links: ["About ICP3A", "Our Team", "Careers", "Press", "Partners", "Investor Relations"],
  },
  {
    title: "Resources",
    links: ["Documentation", "API Reference", "Case Studies", "Blog", "Roadmap", "Status"],
  },
  {
    title: "Legal",
    links: ["Privacy Policy", "Terms of Service", "Cookie Policy", "RERA Compliance", "Data Security"],
  },
];

const cities = ["Delhi NCR", "Mumbai", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Kochi", "Goa"];

export default function Footer() {
  return (
    <footer style={{ background: "#060D1F", borderTop: "1px solid rgba(255,255,255,0.07)" }}>
      <div className="max-w-7xl mx-auto px-6 pt-16 pb-10">

        {/* Top row */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-12 mb-16">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#1D4ED8,#3B82F6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ color: "white", fontWeight: 800, fontSize: "0.95rem", fontFamily: "Space Grotesk,sans-serif" }}>IC</span>
              </div>
              <span style={{ color: "white", fontWeight: 800, fontSize: "1.1rem", fontFamily: "Space Grotesk,sans-serif" }}>ICP3A<span style={{ color: "#F59E0B" }}>.</span></span>
            </div>
            <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.82rem", lineHeight: 1.7, marginBottom: 16 }}>
              Integrated Certified Property Precision Acquisition & Analytics. Every parcel. Certified. Acquired.
            </p>
            <div className="lpi-badge inline-block px-3 py-1 rounded-full mb-4">
              LPI CERTIFIED PLATFORM
            </div>
            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              {["LinkedIn", "Twitter", "WhatsApp"].map(s => (
                <a key={s} href="#" style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.75rem", textDecoration: "none", transition: "color 0.2s" }}
                  onMouseOver={e => (e.currentTarget.style.color = "white")}
                  onMouseOut={e => (e.currentTarget.style.color = "rgba(255,255,255,0.35)")}>{s}</a>
              ))}
            </div>
          </div>

          {/* Link cols */}
          {cols.map(col => (
            <div key={col.title}>
              <h4 style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.7rem", fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 16 }}>{col.title}</h4>
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
                {col.links.map(link => (
                  <li key={link}>
                    <a href="#" style={{ color: "rgba(255,255,255,0.5)", fontSize: "0.82rem", textDecoration: "none", transition: "color 0.2s" }}
                      onMouseOver={e => (e.currentTarget.style.color = "white")}
                      onMouseOut={e => (e.currentTarget.style.color = "rgba(255,255,255,0.5)")}>{link}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Cities strip */}
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.07)", paddingTop: 20, marginBottom: 20 }}>
          <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "0.72rem", marginBottom: 10, letterSpacing: "0.06em" }}>ACTIVE ACQUISITION ZONES</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {cities.map(c => (
              <span key={c} style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.4)", borderRadius: 6, padding: "3px 10px", fontSize: "0.72rem" }}>{c}</span>
            ))}
          </div>
        </div>

        {/* Bottom */}
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.07)", paddingTop: 20, display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "0.78rem", margin: 0 }}>
            © 2026 ICP3A — Integrated Certified Property Precision Acquisition & Analytics. All rights reserved.
          </p>
          <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.72rem", margin: 0 }}>
            LPI Certificates issued under UIG satellite mapping authority · 28 airports · All India
          </p>
        </div>
      </div>
    </footer>
  );
}
