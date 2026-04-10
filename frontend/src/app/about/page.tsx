import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";

const values = [
  { icon: "🛰️", title: "Precision First", desc: "Every land parcel deserves exact boundaries. We built the LPI system because GPS coordinates alone aren't enough — sub-10m satellite LiDAR is the new standard." },
  { icon: "⚡", title: "Speed at Scale", desc: "A property listing shouldn't sit undiscovered for weeks. Our pipeline reaches out within 2 minutes of discovery, 24 hours a day, 365 days a year." },
  { icon: "🔒", title: "Trust Through Transparency", desc: "LPI certificates provide an immutable, verifiable property identity. Every certificate is in our public registry — any buyer, bank, or court can verify it instantly." },
  { icon: "🤝", title: "Agent-Centric", desc: "We don't compete with agents — we empower them. Free LPI licenses, co-branded tools, and revenue share make our agent partners more valuable to their clients." },
];

const milestones = [
  { year: "2023", title: "Research Phase", desc: "Satellite LiDAR data acquisition and parcel grid algorithm development for 10×10m precision mapping across India." },
  { year: "2024", title: "LPI System Launch", desc: "First LPI certificates issued for Delhi NCR airport zone parcels. RERA-compatible format standardised. 5,000+ parcels registered." },
  { year: "2025 Q1", title: "Acquisition Pipeline", desc: "Automated scraping, AI scoring, and WhatsApp outreach pipeline launched. First 100 leads processed within 48 hours of go-live." },
  { year: "2025 Q3", title: "All-India Expansion", desc: "Expanded to 28 airports, 10 cities across 3 tiers. Agent network launched with Bronze/Silver/Gold/Platinum tiers. 1,000+ agent partnerships." },
  { year: "2026", title: "ICP3A Rebrand", desc: "United Investing Group LLC's India division rebrands as ICP3A — Integrated Certified Property Precision Acquisition & Analytics. Full platform launch." },
  { year: "2026+", title: "Global Roadmap", desc: "Southeast Asia expansion: Singapore, Bangkok, Kuala Lumpur, Dubai airport zones. 100,000 LPI certificates target." },
];

const team = [
  { name: "Philip George", title: "Head of Asia Pacific", dept: "Acquisition & Partnerships", initials: "PG", color: "#1D4ED8",
    bio: "Philip leads all property acquisition operations across India and Southeast Asia. With 15+ years in cross-border real estate investment, he has personally closed over 200 airport-zone acquisitions." },
  { name: "Sarah Chen", title: "Chief Technology Officer", dept: "Platform & AI", initials: "SC", color: "#059669",
    bio: "Sarah architected the LPI satellite mapping system and the AI acquisition pipeline. Former Google Maps team. PhD in Geospatial Computing, IIT Delhi." },
  { name: "Arjun Krishnan", title: "Director of Operations", dept: "India Markets", initials: "AK", color: "#8B5CF6",
    bio: "Arjun oversees all Indian city operations, agent partnerships, and regulatory compliance. Former RERA adjudicator. Expert in Indian property law and documentation requirements." },
  { name: "Priya Sharma", title: "Head of Agent Network", dept: "Partnerships", initials: "PS", color: "#F59E0B",
    bio: "Priya built the ICP3A agent partnership programme from 0 to 1,000+ agents across 7 cities. Former JLL India senior director. Specialist in tier-2 city real estate markets." },
];

export default function AboutPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* HERO */}
        <section className="gradient-hero" style={{ paddingTop: 128, paddingBottom: 80 }}>
          <div className="max-w-4xl mx-auto px-6 text-center">
            <p className="section-label mb-4" style={{ color: "#F59E0B" }}>ABOUT ICP3A</p>
            <h1 style={{ color: "white", fontSize: "clamp(2rem,5vw,3.75rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 22, lineHeight: 1.1 }}>
              We map the earth.<br />We certify the land.<br />
              <span className="gradient-text">We close the deal.</span>
            </h1>
            <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "1.05rem", lineHeight: 1.8, maxWidth: 560, margin: "0 auto" }}>
              ICP3A (Integrated Certified Property Precision Acquisition & Analytics) is India's first satellite-grade property certification and automated acquisition platform, operating under United Investing Group LLC.
            </p>
          </div>
        </section>

        {/* MISSION */}
        <section style={{ padding: "88px 0", background: "white" }}>
          <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <p className="section-label mb-4">OUR MISSION</p>
              <h2 style={{ fontSize: "clamp(1.75rem,3.5vw,2.5rem)", fontWeight: 800, color: "#060D1F", letterSpacing: "-0.02em", marginBottom: 20, lineHeight: 1.2 }}>
                A satellite for every parcel on Earth
              </h2>
              <p style={{ color: "#475569", lineHeight: 1.85, fontSize: "0.96rem", marginBottom: 18 }}>
                India has over 330 million land parcels — most with disputed boundaries, outdated surveys, and no digital identity. We believe every parcel deserves a precise, verifiable, satellite-grade identity.
              </p>
              <p style={{ color: "#475569", lineHeight: 1.85, fontSize: "0.96rem", marginBottom: 18 }}>
                The LPI (LiDAR Property Identifier) is that identity. Using our private satellite fleet's LiDAR data, we encode every 10×10m parcel on Earth with a unique, immutable code. We then use that data to find, certify, and acquire the most valuable parcels in India — the ones near airports.
              </p>
              <p style={{ color: "#475569", lineHeight: 1.85, fontSize: "0.96rem" }}>
                Airport-adjacent land is India's fastest-appreciating real estate class. ICP3A's AI-powered pipeline finds it, contacts the owner, and closes the deal — automatically.
              </p>
            </div>
            <div style={{ background: "#060D1F", borderRadius: 20, padding: 40 }}>
              <div className="lpi-badge inline-block px-3 py-1 rounded-full mb-8">LPI REGISTRY STATS — 2026</div>
              {[
                { label: "LPI Certificates Issued", value: "52,400+" },
                { label: "Parcels in Registry", value: "330M+", note: "mappable" },
                { label: "Airport Zones Active", value: "28" },
                { label: "Agent Partners", value: "1,000+" },
                { label: "Cities Covered", value: "10" },
                { label: "Deals Closed", value: "847" },
              ].map(s => (
                <div key={s.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                  <span style={{ color: "rgba(255,255,255,0.5)", fontSize: "0.84rem" }}>{s.label}</span>
                  <span style={{ color: "#F59E0B", fontWeight: 800, fontSize: "1.05rem", fontFamily: "Space Grotesk,sans-serif" }}>{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* VALUES */}
        <section style={{ padding: "88px 0", background: "#F8FAFC" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3">OUR VALUES</p>
              <h2 style={{ fontSize: "clamp(1.75rem,3.5vw,2.5rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>What we stand for</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map(v => (
                <div key={v.title} className="card-glow" style={{ borderRadius: 16, padding: 28, border: "1px solid #E2E8F0", background: "white" }}>
                  <div style={{ fontSize: "2rem", marginBottom: 16 }}>{v.icon}</div>
                  <h3 style={{ fontWeight: 700, color: "#0F172A", marginBottom: 10, fontSize: "1rem" }}>{v.title}</h3>
                  <p style={{ color: "#64748B", fontSize: "0.86rem", lineHeight: 1.7, margin: 0 }}>{v.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* MILESTONES */}
        <section style={{ padding: "88px 0", background: "white" }}>
          <div className="max-w-4xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3">TIMELINE</p>
              <h2 style={{ fontSize: "clamp(1.75rem,3.5vw,2.5rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>Building ICP3A</h2>
            </div>
            <div style={{ position: "relative" }}>
              <div style={{ position: "absolute", left: 19, top: 0, bottom: 0, width: 2, background: "#E2E8F0" }} />
              <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
                {milestones.map((m, i) => (
                  <div key={m.year} style={{ display: "flex", gap: 24, paddingLeft: 0 }}>
                    <div className="timeline-dot" style={{ zIndex: 1, flexShrink: 0 }}>{i + 1}</div>
                    <div style={{ paddingTop: 6 }}>
                      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 6 }}>
                        <span style={{ background: "#EFF6FF", color: "#1D4ED8", fontSize: "0.72rem", fontWeight: 700, borderRadius: 4, padding: "2px 8px" }}>{m.year}</span>
                        <h3 style={{ fontWeight: 700, color: "#0F172A", fontSize: "1rem", margin: 0 }}>{m.title}</h3>
                      </div>
                      <p style={{ color: "#64748B", fontSize: "0.88rem", lineHeight: 1.7, margin: 0 }}>{m.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* TEAM */}
        <section style={{ padding: "88px 0", background: "#F8FAFC" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3">THE TEAM</p>
              <h2 style={{ fontSize: "clamp(1.75rem,3.5vw,2.5rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>The people behind ICP3A</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {team.map(t => (
                <div key={t.name} className="card-glow" style={{ borderRadius: 16, padding: 28, border: "1px solid #E2E8F0", background: "white", display: "flex", gap: 20 }}>
                  <div style={{ width: 56, height: 56, borderRadius: "50%", background: t.color, display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 800, fontSize: "1rem", flexShrink: 0 }}>{t.initials}</div>
                  <div>
                    <h3 style={{ fontWeight: 800, color: "#0F172A", fontSize: "1rem", marginBottom: 2 }}>{t.name}</h3>
                    <p style={{ color: t.color, fontWeight: 600, fontSize: "0.82rem", marginBottom: 2 }}>{t.title}</p>
                    <p style={{ color: "#94A3B8", fontSize: "0.75rem", marginBottom: 10 }}>{t.dept}</p>
                    <p style={{ color: "#64748B", fontSize: "0.85rem", lineHeight: 1.7, margin: 0 }}>{t.bio}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section style={{ background: "linear-gradient(135deg,#060D1F,#0C1A3A)", padding: "72px 0" }}>
          <div className="max-w-3xl mx-auto px-6 text-center">
            <h2 style={{ color: "white", fontSize: "clamp(1.6rem,4vw,2.5rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>Join the ICP3A network</h2>
            <p style={{ color: "rgba(255,255,255,0.5)", marginBottom: 36 }}>Whether you're a property owner, agent, or investor — there's a place for you in the ICP3A ecosystem.</p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
              <Link href="/contact" className="btn-gold">Get in Touch →</Link>
              <Link href="/services" className="btn-outline">Explore Services</Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
