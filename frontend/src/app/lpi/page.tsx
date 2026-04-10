import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";

const codes = [
  { seg: "LPI", label: "System", color: "#3B82F6" },
  { seg: "IN", label: "Country", color: "#10B981" },
  { seg: "DL", label: "State", color: "#8B5CF6" },
  { seg: "028556", label: "Grid X (lon)", color: "#F59E0B" },
  { seg: "077100", label: "Grid Y (lat)", color: "#EF4444" },
  { seg: "0042", label: "Sub-parcel", color: "#0891B2" },
];

const requiredDocs = [
  { name: "Sale Deed / Title Deed", mandatory: true, note: "Proof of ownership chain" },
  { name: "Khata Certificate", mandatory: true, note: "Municipal property record" },
  { name: "Encumbrance Certificate", mandatory: true, note: "Confirms no liens/mortgages" },
  { name: "Property Tax Receipts", mandatory: true, note: "Last 3 years" },
  { name: "NOC from Society/Authority", mandatory: true, note: "No Objection Certificate" },
  { name: "Aadhar Card / PAN Card", mandatory: true, note: "Owner identity verification" },
  { name: "LPI Certificate ✅", mandatory: true, note: "MANDATORY — issued by ICP3A" },
  { name: "RERA Certificate", mandatory: false, note: "For RERA-registered properties" },
  { name: "Mutation Certificate", mandatory: false, note: "If ownership transferred" },
  { name: "Building Plan Approval", mandatory: false, note: "For constructed properties" },
];

const steps = [
  { n: 1, title: "Submit Property Details", desc: "Provide your property address, area, and identity documents via the form below or via WhatsApp to Philip George." },
  { n: 2, title: "Satellite Scan", desc: "Our system looks up the exact 10×10m grid cell from the LiDAR point cloud dataset. Takes under 60 seconds." },
  { n: 3, title: "LPI Code Generated", desc: "Your unique LPI code is generated: LPI-IN-[STATE]-[GRIDX]-[GRIDY]-[SUB]. Registered to your name in the ICP3A parcel registry." },
  { n: 4, title: "Certificate Issued", desc: "PDF certificate issued with QR code for instant verification. Valid as supporting document for RERA, bank submissions, and property sales." },
  { n: 5, title: "Annual Registry Update", desc: "Your LPI entry is updated annually. Ownership transfers, splits, and area changes are all tracked in the immutable LPI registry." },
];

export default function LPIPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* HERO */}
        <section className="gradient-hero" style={{ paddingTop: 128, paddingBottom: 80 }}>
          <div className="max-w-4xl mx-auto px-6 text-center">
            <div className="lpi-badge inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8">🛰️ LIDAR PROPERTY IDENTIFIER</div>
            <h1 style={{ color: "white", fontSize: "clamp(2rem,5vw,3.75rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 20, lineHeight: 1.1 }}>
              Your land.<br />
              <span className="gradient-text">Certified from space.</span>
            </h1>
            <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "1.05rem", lineHeight: 1.8, maxWidth: 560, margin: "0 auto 40px" }}>
              The LPI (LiDAR Property Identifier) is a unique satellite-grade identity for every 10×10m parcel on Earth. More precise than any ground survey. Verifiable instantly. Valid in perpetuity.
            </p>
            <Link href="/contact" className="btn-gold" style={{ fontSize: "1rem", padding: "14px 36px" }}>Apply for LPI Certificate →</Link>
          </div>
        </section>

        {/* CODE ANATOMY */}
        <section style={{ padding: "80px 0", background: "#060D1F" }}>
          <div className="max-w-4xl mx-auto px-6 text-center">
            <p className="section-label mb-4" style={{ color: "#F59E0B" }}>LPI CODE STRUCTURE</p>
            <h2 style={{ color: "white", fontSize: "clamp(1.5rem,3vw,2.25rem)", fontWeight: 700, marginBottom: 40, letterSpacing: "-0.02em" }}>
              Anatomy of an LPI code
            </h2>
            <div style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 16, padding: "32px 40px", marginBottom: 40 }}>
              <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 0, marginBottom: 20 }}>
                {codes.map((c, i) => (
                  <span key={c.seg}>
                    <span style={{ color: c.color, fontFamily: "Space Grotesk,monospace", fontSize: "clamp(1.2rem,3vw,2rem)", fontWeight: 800, letterSpacing: "0.04em" }}>{c.seg}</span>
                    {i < codes.length - 1 && <span style={{ color: "rgba(255,255,255,0.25)", fontSize: "clamp(1.2rem,3vw,2rem)", margin: "0 2px" }}>-</span>}
                  </span>
                ))}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 12 }}>
                {codes.map(c => (
                  <div key={c.seg} style={{ textAlign: "center" }}>
                    <div style={{ background: `${c.color}22`, border: `1px solid ${c.color}44`, color: c.color, borderRadius: 6, padding: "4px 12px", fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.06em" }}>{c.seg}</div>
                    <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.68rem", marginTop: 4 }}>{c.label}</div>
                  </div>
                ))}
              </div>
            </div>
            <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.84rem", lineHeight: 1.7 }}>
              Grid resolution: 0.00009° (~10m) per cell. Over 10 trillion unique cells globally. India coverage: complete.
            </p>
          </div>
        </section>

        {/* PROCESS */}
        <section style={{ padding: "80px 0", background: "white" }}>
          <div className="max-w-4xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3">PROCESS</p>
              <h2 style={{ fontSize: "clamp(1.5rem,3vw,2.25rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>How to get your LPI Certificate</h2>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
              {steps.map(s => (
                <div key={s.n} style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
                  <div className="timeline-dot">{s.n}</div>
                  <div style={{ paddingTop: 6 }}>
                    <h3 style={{ fontWeight: 700, color: "#0F172A", marginBottom: 6, fontSize: "1rem" }}>{s.title}</h3>
                    <p style={{ color: "#64748B", fontSize: "0.88rem", lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* DOCUMENT CHECKLIST */}
        <section style={{ padding: "80px 0", background: "#F8FAFC" }}>
          <div className="max-w-3xl mx-auto px-6">
            <div className="text-center mb-12">
              <p className="section-label mb-3">DOCUMENT CHECKLIST</p>
              <h2 style={{ fontSize: "clamp(1.5rem,3vw,2.25rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>Required for full acquisition approval</h2>
              <p style={{ color: "#64748B", marginTop: 12, fontSize: "0.92rem" }}>All 10 documents must be submitted. LPI Certificate is mandatory — the pipeline cannot proceed without it.</p>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {requiredDocs.map(d => (
                <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 18px", borderRadius: 10, border: "1px solid #E2E8F0", background: "white" }}>
                  <div style={{ width: 28, height: 28, borderRadius: "50%", background: d.mandatory ? "#DCFCE7" : "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: "0.9rem" }}>
                    {d.mandatory ? "✓" : "○"}
                  </div>
                  <div style={{ flex: 1 }}>
                    <span style={{ fontWeight: d.name.includes("LPI") ? 800 : 600, color: d.name.includes("LPI") ? "#1D4ED8" : "#0F172A", fontSize: "0.9rem" }}>{d.name}</span>
                    <span style={{ color: "#94A3B8", fontSize: "0.78rem", marginLeft: 8 }}>{d.note}</span>
                  </div>
                  {d.mandatory && (
                    <span style={{ background: d.name.includes("LPI") ? "#EFF6FF" : "#F0FDF4", color: d.name.includes("LPI") ? "#1D4ED8" : "#16A34A", fontSize: "0.65rem", fontWeight: 700, borderRadius: 4, padding: "2px 8px", letterSpacing: "0.06em", flexShrink: 0 }}>
                      {d.name.includes("LPI") ? "MANDATORY" : "REQUIRED"}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* PRICING */}
        <section style={{ padding: "80px 0", background: "#060D1F" }}>
          <div className="max-w-4xl mx-auto px-6">
            <div className="text-center mb-14">
              <p className="section-label mb-3" style={{ color: "#F59E0B" }}>LPI PRICING</p>
              <h2 style={{ color: "white", fontSize: "clamp(1.5rem,3vw,2.25rem)", fontWeight: 700, letterSpacing: "-0.02em" }}>Simple, transparent certificate fees</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { name: "Individual Certificate", price: "₹2,500", period: "one-time", desc: "Single parcel LPI code + PDF certificate + QR verification. Valid permanently.", color: "#3B82F6" },
                { name: "Annual Registry", price: "₹12,000", period: "per year", desc: "Keep your LPI parcel in the active registry with annual updates, ownership transfers, and area changes.", color: "#F59E0B" },
                { name: "Agent License", price: "₹0", period: "for partners", desc: "Free LPI license for RERA-registered agent partners. Value: ₹2,50,000/year. Apply via agent portal.", color: "#10B981" },
              ].map(p => (
                <div key={p.name} className="stat-card" style={{ borderRadius: 16, padding: 28, border: `1px solid ${p.color}33` }}>
                  <div style={{ color: p.color, fontSize: "2rem", fontWeight: 800, fontFamily: "Space Grotesk,sans-serif", marginBottom: 4 }}>{p.price}</div>
                  <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.8rem", marginBottom: 12 }}>{p.period}</div>
                  <h3 style={{ color: "white", fontWeight: 700, fontSize: "1rem", marginBottom: 10 }}>{p.name}</h3>
                  <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.84rem", lineHeight: 1.65, margin: 0 }}>{p.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section style={{ background: "linear-gradient(135deg,#060D1F,#0C1A3A)", padding: "72px 0" }}>
          <div className="max-w-2xl mx-auto px-6 text-center">
            <h2 style={{ color: "white", fontSize: "clamp(1.6rem,4vw,2.5rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>Apply for your LPI Certificate</h2>
            <p style={{ color: "rgba(255,255,255,0.5)", marginBottom: 36 }}>Contact Philip George directly or submit your property details below. Certificate issued within 24 hours.</p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
              <Link href="/contact" className="btn-gold">Apply Now →</Link>
              <Link href="/pricing" className="btn-outline">View All Pricing</Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
