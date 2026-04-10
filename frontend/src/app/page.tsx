import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";

const stats = [
  { value: "28", label: "Airport Zones", sub: "Across India" },
  { value: "330M+", label: "Land Parcels", sub: "Mappable with LPI" },
  { value: "10×10m", label: "Grid Precision", sub: "Satellite-grade accuracy" },
  { value: "<2min", label: "First Contact", sub: "After lead discovery" },
];

const features = [
  { icon: "🛰️", title: "LPI Satellite Certification", badge: "PROPRIETARY",
    desc: "Every 10×10m parcel on Earth gets a unique LiDAR Property Identifier — India's first satellite-grade boundary certification, more precise than any government survey." },
  { icon: "🤖", title: "AI-Powered Lead Scoring", badge: "CLAUDE AI",
    desc: "Claude AI scores every lead 0–100 across 5 weighted factors. Only high-quality leads enter your outreach queue. No wasted calls." },
  { icon: "✈️", title: "Airport Zone Intelligence", badge: "28 AIRPORTS",
    desc: "5km radius geofencing around all 28 major Indian airports — India's fastest-appreciating real estate, mapped and prioritised automatically." },
  { icon: "📱", title: "WhatsApp Automation", badge: "TWILIO",
    desc: "Instant outreach as Philip George. Day 0 contact, Day 3 follow-up, Day 7 nurture — all automated, AI-personalised, zero manual effort." },
  { icon: "📋", title: "Document Verification", badge: "AI VISION",
    desc: "Claude Vision AI analyses Sale Deeds, Khata Certificates, and LPI Certificates. Completeness checks run in seconds. LPI is mandatory — pipeline blocked without it." },
  { icon: "🏢", title: "11-Stage CRM Pipeline", badge: "HUBSPOT",
    desc: "From new_lead to closed_won, every stage triggers automated actions. HubSpot synced. Google Drive per lead. Make.com + n8n orchestrated." },
];

const steps = [
  { n: "01", title: "Discover", desc: "Scrapers pull listings from 99acres, MagicBricks, NoBroker and Housing.com across all airport zones. Import your own leads via CSV, Excel, or JSON." },
  { n: "02", title: "Score", desc: "Claude AI scores every lead 0–100 in under 3 seconds — contact quality, freshness, location tier, responsiveness, and document readiness." },
  { n: "03", title: "Reach Out", desc: "WhatsApp + email fires within 2 minutes of discovery. Day 3 and Day 7 follow-ups queued automatically. Zero manual work required." },
  { n: "04", title: "Qualify", desc: "AI classifies every reply: Interested, Not Interested, or More Info. Interested owners auto-advance to qualified and receive a document checklist." },
  { n: "05", title: "Verify", desc: "Owner uploads documents. Claude Vision AI analyses each one. LPI Certificate mandatory — pipeline blocked until confirmed valid." },
  { n: "06", title: "Close", desc: "Philip's team visits. HubSpot deal created. Site visit scheduled automatically. Closed deals feed back into the LPI parcel registry." },
];

const testimonials = [
  { name: "Rajesh Mehta", role: "Property Owner · Mahipalpur, Delhi", initials: "RM", color: "#1D4ED8",
    quote: "Philip George reached out within hours of my listing going live. The LPI certification gave me confidence the valuation was fair and the process was transparent." },
  { name: "Priya Nair", role: "Real Estate Agent · Bengaluru", initials: "PN", color: "#059669",
    quote: "The ICP3A agent partnership transformed my business. The free LPI license alone is worth ₹2.5 lakh a year. I've referred 12 properties in 3 months." },
  { name: "Suresh Iyer", role: "NRI Investor · Dubai", initials: "SI", color: "#F59E0B",
    quote: "As an NRI acquiring near Kochi airport, I needed precision documentation. ICP3A handled everything remotely — LPI, legal check, deal closed in 21 days." },
];

const cities = [
  { name: "Delhi NCR", airport: "IGI Airport", tier: "Tier 1" },
  { name: "Mumbai", airport: "CSIA Airport", tier: "Tier 1" },
  { name: "Bengaluru", airport: "Kempegowda Intl", tier: "Tier 1" },
  { name: "Hyderabad", airport: "Rajiv Gandhi Intl", tier: "Tier 2" },
  { name: "Chennai", airport: "Chennai Intl", tier: "Tier 2" },
  { name: "Kolkata", airport: "NSCB Intl", tier: "Tier 2" },
  { name: "Pune", airport: "Pune Intl", tier: "Tier 2" },
  { name: "Ahmedabad", airport: "SVP Intl", tier: "Tier 3" },
  { name: "Goa", airport: "Dabolim Intl", tier: "Tier 3" },
  { name: "Kochi", airport: "Cochin Intl", tier: "Tier 3" },
];

const tierColor = (t: string) =>
  t === "Tier 1" ? { bg: "#1D4ED811", border: "#1D4ED833", text: "#3B82F6" }
  : t === "Tier 2" ? { bg: "#05966911", border: "#05966933", text: "#10B981" }
  : { bg: "#F59E0B11", border: "#F59E0B33", text: "#F59E0B" };

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        {/* HERO */}
        <section className="gradient-hero" style={{ paddingTop: 136, paddingBottom: 96 }}>
          <div className="max-w-6xl mx-auto px-6 text-center">
            <div className="lpi-badge inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8">
              🛰️ INDIA'S FIRST SATELLITE-GRADE PROPERTY CERTIFICATION PLATFORM
            </div>
            <h1 style={{ color: "white", fontSize: "clamp(2.6rem,6vw,4.75rem)", fontWeight: 800, lineHeight: 1.08, marginBottom: 24, letterSpacing: "-0.03em" }}>
              Every Parcel.<br />
              <span className="gradient-text">Certified. Acquired.</span>
            </h1>
            <p style={{ color: "rgba(255,255,255,0.6)", fontSize: "clamp(1rem,2.2vw,1.2rem)", maxWidth: 600, margin: "0 auto 44px", lineHeight: 1.75 }}>
              ICP3A maps, certifies, and acquires properties within 5km of all 28 Indian airports using LiDAR satellite precision and an AI-powered acquisition pipeline.
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center", marginBottom: 56 }}>
              <Link href="/contact" className="btn-gold" style={{ fontSize: "1rem", padding: "14px 34px" }}>Start Acquiring →</Link>
              <Link href="/lpi" className="btn-outline" style={{ fontSize: "1rem", padding: "14px 34px" }}>Get LPI Certificate</Link>
            </div>
            <div style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.09)", borderRadius: 12, padding: "14px 28px", display: "inline-block" }}>
              <p style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.7rem", marginBottom: 6, letterSpacing: "0.12em" }}>SAMPLE LPI CERTIFICATE CODE</p>
              <code style={{ color: "#F59E0B", fontFamily: "Space Grotesk,monospace", fontSize: "1.05rem", letterSpacing: "0.06em" }}>LPI-IN-DL-028556-077100-0042</code>
            </div>
          </div>
        </section>

        {/* STATS */}
        <section style={{ background: "#07101F", padding: "56px 0" }}>
          <div className="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-5">
            {stats.map(s => (
              <div key={s.label} className="stat-card text-center">
                <div style={{ color: "#F59E0B", fontSize: "2.4rem", fontWeight: 800, fontFamily: "Space Grotesk,sans-serif", lineHeight: 1 }}>{s.value}</div>
                <div style={{ color: "white", fontWeight: 600, marginTop: 8, fontSize: "0.92rem" }}>{s.label}</div>
                <div style={{ color: "rgba(255,255,255,0.38)", fontSize: "0.76rem", marginTop: 3 }}>{s.sub}</div>
              </div>
            ))}
          </div>
        </section>

        {/* FEATURES */}
        <section style={{ padding: "96px 0", background: "white" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-16">
              <p className="section-label mb-3">PLATFORM CAPABILITIES</p>
              <h2 style={{ fontSize: "clamp(1.75rem,4vw,2.75rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>
                The complete property acquisition stack
              </h2>
              <p style={{ color: "#64748B", maxWidth: 520, margin: "14px auto 0", fontSize: "1rem", lineHeight: 1.7 }}>
                From satellite mapping to WhatsApp outreach to deal closing — fully automated.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map(f => (
                <div key={f.title} className="card-glow" style={{ borderRadius: 16, padding: 30, border: "1px solid #E2E8F0" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                    <div className="feature-icon" style={{ fontSize: "1.4rem" }}>{f.icon}</div>
                    <span style={{ background: "#EFF6FF", color: "#1D4ED8", fontSize: "0.62rem", fontWeight: 700, letterSpacing: "0.1em", borderRadius: 4, padding: "2px 7px" }}>{f.badge}</span>
                  </div>
                  <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#0F172A", marginBottom: 8 }}>{f.title}</h3>
                  <p style={{ color: "#64748B", fontSize: "0.86rem", lineHeight: 1.7, margin: 0 }}>{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section style={{ padding: "96px 0", background: "#F8FAFC" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-16">
              <p className="section-label mb-3">HOW IT WORKS</p>
              <h2 style={{ fontSize: "clamp(1.75rem,4vw,2.75rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>
                Listing to closed deal in 21 days
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {steps.map(s => (
                <div key={s.n} style={{ display: "flex", gap: 16 }}>
                  <div className="timeline-dot">{s.n}</div>
                  <div>
                    <h3 style={{ fontWeight: 700, color: "#0F172A", marginBottom: 6, fontSize: "1rem" }}>{s.title}</h3>
                    <p style={{ color: "#64748B", fontSize: "0.86rem", lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* AIRPORT COVERAGE */}
        <section style={{ padding: "96px 0", background: "#060D1F" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3" style={{ color: "#F59E0B" }}>COVERAGE MAP</p>
              <h2 style={{ fontSize: "clamp(1.75rem,4vw,2.75rem)", fontWeight: 700, color: "white", letterSpacing: "-0.02em" }}>28 airports. All India. Active now.</h2>
              <p style={{ color: "rgba(255,255,255,0.45)", maxWidth: 480, margin: "12px auto 0", lineHeight: 1.7 }}>
                Every property within 5km of a major Indian airport is auto-discovered, scored, and queued for acquisition.
              </p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {cities.map(c => {
                const col = tierColor(c.tier);
                return (
                  <div key={c.name} className="stat-card" style={{ padding: 18 }}>
                    <div style={{ marginBottom: 8 }}>
                      <span style={{ background: col.bg, border: `1px solid ${col.border}`, color: col.text, fontSize: "0.62rem", fontWeight: 700, letterSpacing: "0.08em", borderRadius: 4, padding: "2px 7px" }}>{c.tier}</span>
                    </div>
                    <div style={{ color: "white", fontWeight: 700, fontSize: "0.9rem" }}>{c.name}</div>
                    <div style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.7rem", marginTop: 3 }}>{c.airport}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* TESTIMONIALS */}
        <section style={{ padding: "96px 0", background: "white" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3">TESTIMONIALS</p>
              <h2 style={{ fontSize: "clamp(1.75rem,4vw,2.75rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>
                Trusted by owners, agents & NRI investors
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-7">
              {testimonials.map(t => (
                <div key={t.name} className="card-glow" style={{ borderRadius: 20, padding: 30, border: "1px solid #E2E8F0" }}>
                  <div style={{ fontSize: "2.2rem", color: "#E2E8F0", marginBottom: 12, lineHeight: 1 }}>"</div>
                  <p style={{ color: "#334155", lineHeight: 1.75, fontSize: "0.9rem", marginBottom: 22 }}>{t.quote}</p>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 38, height: 38, borderRadius: "50%", background: t.color, display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 700, fontSize: "0.82rem" }}>{t.initials}</div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: "0.86rem", color: "#0F172A" }}>{t.name}</div>
                      <div style={{ color: "#94A3B8", fontSize: "0.75rem" }}>{t.role}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FINAL CTA */}
        <section style={{ background: "linear-gradient(135deg,#060D1F 0%,#0C1A3A 100%)", padding: "80px 0" }}>
          <div className="max-w-3xl mx-auto px-6 text-center">
            <div className="lpi-badge inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6">🚀 START TODAY</div>
            <h2 style={{ color: "white", fontSize: "clamp(1.75rem,4vw,2.75rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>
              Launch your first acquisition campaign
            </h2>
            <p style={{ color: "rgba(255,255,255,0.5)", fontSize: "1rem", lineHeight: 1.75, marginBottom: 40 }}>
              Import your leads, run a scrape campaign, and let the AI pipeline handle outreach. First 1,000 leads cost under ₹1,200 to contact.
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center" }}>
              <Link href="/contact" className="btn-gold" style={{ fontSize: "1rem", padding: "14px 36px" }}>Get Started Free →</Link>
              <Link href="/pricing" className="btn-outline" style={{ fontSize: "1rem", padding: "14px 36px" }}>View Pricing</Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
