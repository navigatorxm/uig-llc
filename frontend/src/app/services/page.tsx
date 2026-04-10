import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";

const services = [
  {
    icon: "🛰️",
    tag: "CORE SERVICE",
    title: "LPI Certification",
    subtitle: "LiDAR Property Identifier — India's satellite standard",
    desc: "Every 10×10m parcel on Earth is geo-encoded with a unique LPI code using ICP3A's satellite LiDAR mapping technology. LPI certificates are legally supporting documentation for property sales, bank loans, and RERA submissions.",
    features: [
      "Unique code per 10×10m parcel (e.g. LPI-IN-DL-028556-077100-0042)",
      "Sub-10m satellite accuracy using LiDAR point cloud data",
      "Instant verification via QR code or API",
      "Compatible with RERA, bank submissions, and legal filings",
      "Airport zone premium marking (5km radius)",
      "Annual registry subscription with ownership chain",
    ],
    pricing: "₹2,500 one-time + ₹12,000/year registry",
    color: "#F59E0B",
  },
  {
    icon: "🏠",
    tag: "ACQUISITION",
    title: "Property Acquisition Pipeline",
    subtitle: "AI-powered end-to-end property sourcing and closing",
    desc: "ICP3A's fully automated pipeline discovers property listings across all major Indian portals, scores them with Claude AI, reaches out within 2 minutes, and manages the entire 11-stage journey from new lead to closed deal.",
    features: [
      "Scraping: 99acres, MagicBricks, NoBroker, Housing.com, CommonFloor",
      "AI lead scoring 0–100 (Claude claude-sonnet-4-6) — 5 weighted factors",
      "WhatsApp outreach via Twilio as Philip George within 2 min",
      "Day 0 / Day 3 / Day 7 / Day 14 automated follow-up sequences",
      "11-stage CRM pipeline with HubSpot bidirectional sync",
      "Document collection + Google Drive storage per lead",
      "AI document verification via Claude Vision API",
      "Approved leads → site visit invitation → deal creation",
    ],
    pricing: "Commission-based + platform subscription",
    color: "#1D4ED8",
  },
  {
    icon: "✈️",
    tag: "INTELLIGENCE",
    title: "Airport Zone Mapping",
    subtitle: "5km geofencing around all 28 major Indian airports",
    desc: "ICP3A's geofencing engine identifies every property within a 5km radius of any Indian airport using the Haversine formula. Airport-adjacent properties are India's fastest-appreciating real estate and receive priority scoring.",
    features: [
      "28 airports indexed with precise lat/lon coordinates",
      "Haversine-formula distance calculation for every property",
      "Tier 1 / Tier 2 / Tier 3 zone classification",
      "Priority queue for sub-2km airport-adjacent properties",
      "GIFT City, Aerocity, BKC zone overlays",
      "Automatic geofence tag on all scraped listings",
      "NRI targeting zones for international investor campaigns",
    ],
    pricing: "Included in Acquisition pipeline subscription",
    color: "#8B5CF6",
  },
  {
    icon: "🤝",
    tag: "PARTNERSHIPS",
    title: "Real Estate Agent Network",
    subtitle: "Bronze → Silver → Gold → Platinum agent partnership tiers",
    desc: "ICP3A partners with RERA-registered real estate agents across India, providing them with free LPI licenses (worth ₹2.5L/year), co-branded listing tools, and a revenue share on every successful acquisition they facilitate.",
    features: [
      "Free LPI Agent License (value: ₹2,50,000/year) for onboarded agents",
      "RERA registration verification during onboarding",
      "Bronze / Silver / Gold / Platinum tiers based on conversions",
      "Co-branded property listings with LPI certification badge",
      "Dedicated WhatsApp + email outreach to top agent firms",
      "Agent portal with pipeline tracking and commission dashboard",
      "City-specific campaigns: 7 cities, top 50 firms per city",
    ],
    pricing: "Revenue share model — no upfront agent fees",
    color: "#059669",
  },
  {
    icon: "📄",
    tag: "VERIFICATION",
    title: "Document Verification Suite",
    subtitle: "AI-powered legal document analysis using Claude Vision",
    desc: "ICP3A's verification suite uses Claude Vision API to analyse uploaded property documents in seconds — checking authenticity, extracting key fields, and confirming LPI certificate validity before any deal proceeds.",
    features: [
      "Supports 12 document types (Sale Deed, Khata, Encumbrance, etc.)",
      "Mandatory: LPI Certificate — pipeline blocked until confirmed",
      "Claude Vision AI analysis with confidence score per document",
      "Encumbrance status check and ownership chain validation",
      "Google Drive folder auto-created per lead",
      "Upload link sent to owner via WhatsApp",
      "Philip George notified by email when all docs complete",
      "48-hour SLA from upload to verification decision",
    ],
    pricing: "Included in Acquisition pipeline subscription",
    color: "#DC2626",
  },
  {
    icon: "📊",
    tag: "ANALYTICS",
    title: "Acquisition Analytics Dashboard",
    subtitle: "Live pipeline KPIs, funnel conversion rates, outreach performance",
    desc: "A real-time Next.js dashboard gives the ICP3A team complete visibility into every stage of the acquisition funnel — from scrape volume to response rates, document completion, deal velocity, and HubSpot pipeline value.",
    features: [
      "11-column Kanban board with live lead counts",
      "4 headline KPIs: Total Leads, Contact Rate, Docs Received, Deals",
      "Recharts conversion funnel: new_lead → closed_won",
      "WhatsApp delivery rate + email open rate tracking",
      "City-wise and portal-wise lead source breakdown",
      "AI score distribution chart (bucket by 0–40 / 40–70 / 70–100)",
      "Lead score card: 5-factor breakdown per individual lead",
      "HubSpot deal pipeline value — live sync",
    ],
    pricing: "Included in all plans",
    color: "#0891B2",
  },
];

export default function ServicesPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* HERO */}
        <section className="gradient-hero" style={{ paddingTop: 128, paddingBottom: 72 }}>
          <div className="max-w-4xl mx-auto px-6 text-center">
            <p className="section-label mb-4" style={{ color: "#F59E0B" }}>SERVICES</p>
            <h1 style={{ color: "white", fontSize: "clamp(2rem,5vw,3.75rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 20, lineHeight: 1.1 }}>
              Everything you need to acquire at scale
            </h1>
            <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "1.1rem", lineHeight: 1.75, maxWidth: 560, margin: "0 auto" }}>
              Six integrated services. One automated pipeline. From satellite mapping to closed deal.
            </p>
          </div>
        </section>

        {/* SERVICES */}
        <section style={{ padding: "80px 0", background: "white" }}>
          <div className="max-w-6xl mx-auto px-6" style={{ display: "flex", flexDirection: "column", gap: 64 }}>
            {services.map((s, i) => (
              <div key={s.title} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 56, alignItems: "start" }}>
                {/* Left: info (alternate sides) */}
                <div style={{ order: i % 2 === 0 ? 0 : 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                    <span style={{ fontSize: "1.5rem" }}>{s.icon}</span>
                    <span style={{ background: "#F1F5F9", color: "#64748B", fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.12em", borderRadius: 4, padding: "3px 8px" }}>{s.tag}</span>
                  </div>
                  <h2 style={{ fontSize: "1.75rem", fontWeight: 800, color: "#0F172A", letterSpacing: "-0.02em", marginBottom: 6 }}>{s.title}</h2>
                  <p style={{ color: s.color, fontWeight: 600, fontSize: "0.88rem", marginBottom: 16 }}>{s.subtitle}</p>
                  <p style={{ color: "#475569", lineHeight: 1.8, fontSize: "0.92rem", marginBottom: 24 }}>{s.desc}</p>
                  <div style={{ background: "#F8FAFC", borderRadius: 10, padding: "10px 14px", display: "inline-block" }}>
                    <span style={{ color: "#64748B", fontSize: "0.75rem", fontWeight: 600 }}>PRICING: </span>
                    <span style={{ color: "#0F172A", fontSize: "0.82rem", fontWeight: 600 }}>{s.pricing}</span>
                  </div>
                </div>

                {/* Right: features card */}
                <div style={{ order: i % 2 === 0 ? 1 : 0 }}>
                  <div className="card-glow" style={{ borderRadius: 16, padding: 28, border: `1px solid ${s.color}22`, background: `${s.color}06` }}>
                    <h4 style={{ fontSize: "0.78rem", fontWeight: 700, letterSpacing: "0.1em", color: s.color, marginBottom: 16, textTransform: "uppercase" }}>WHAT'S INCLUDED</h4>
                    <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
                      {s.features.map(f => (
                        <li key={f} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                          <span style={{ color: s.color, marginTop: 2, flexShrink: 0, fontSize: "0.9rem" }}>✓</span>
                          <span style={{ color: "#334155", fontSize: "0.86rem", lineHeight: 1.6 }}>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section style={{ background: "linear-gradient(135deg,#060D1F,#0C1A3A)", padding: "72px 0" }}>
          <div className="max-w-3xl mx-auto px-6 text-center">
            <h2 style={{ color: "white", fontSize: "clamp(1.6rem,4vw,2.5rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>
              Ready to activate the full stack?
            </h2>
            <p style={{ color: "rgba(255,255,255,0.5)", marginBottom: 36, lineHeight: 1.75 }}>
              All 6 services are live and ready. Setup takes under 2 hours.
            </p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
              <Link href="/pricing" className="btn-gold">See Pricing →</Link>
              <Link href="/contact" className="btn-outline">Talk to Philip George</Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
