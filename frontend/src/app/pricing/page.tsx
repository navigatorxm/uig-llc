import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";

const plans = [
  {
    name: "Starter",
    tag: "FOR INDIVIDUAL AGENTS",
    price: "₹4,999",
    period: "/month",
    desc: "Perfect for independent agents and small investors getting started with LPI certification.",
    cta: "Start Free Trial",
    href: "/contact",
    featured: false,
    color: "#1D4ED8",
    features: [
      { text: "5 LPI Certificates/month", included: true },
      { text: "Import up to 200 leads", included: true },
      { text: "WhatsApp outreach (200 msgs/month)", included: true },
      { text: "Email outreach (500 emails/month)", included: true },
      { text: "AI lead scoring (Claude)", included: true },
      { text: "Basic analytics dashboard", included: true },
      { text: "1 city coverage", included: true },
      { text: "HubSpot sync", included: false },
      { text: "Document verification (AI)", included: false },
      { text: "Agent partnership portal", included: false },
      { text: "Multi-city campaigns", included: false },
      { text: "Dedicated account manager", included: false },
    ],
    highlight: null,
  },
  {
    name: "Professional",
    tag: "MOST POPULAR",
    price: "₹19,999",
    period: "/month",
    desc: "For growing acquisition teams running active campaigns across multiple airport zones.",
    cta: "Get Started",
    href: "/contact",
    featured: true,
    color: "#F59E0B",
    features: [
      { text: "25 LPI Certificates/month", included: true },
      { text: "Import unlimited leads", included: true },
      { text: "WhatsApp outreach (2,000 msgs/month)", included: true },
      { text: "Email outreach (unlimited)", included: true },
      { text: "AI lead scoring + personalisation", included: true },
      { text: "Full analytics + funnel dashboard", included: true },
      { text: "3 cities coverage", included: true },
      { text: "HubSpot bidirectional sync", included: true },
      { text: "AI document verification", included: true },
      { text: "Agent partnership portal", included: true },
      { text: "Multi-city campaigns", included: false },
      { text: "Dedicated account manager", included: false },
    ],
    highlight: "Save ₹60,000/year vs monthly",
  },
  {
    name: "Enterprise",
    tag: "FOR LARGE TEAMS",
    price: "Custom",
    period: "",
    desc: "Full-scale deployment across all 28 airport zones with dedicated support and white-labelling.",
    cta: "Contact Sales",
    href: "/contact",
    featured: false,
    color: "#8B5CF6",
    features: [
      { text: "Unlimited LPI Certificates", included: true },
      { text: "Import unlimited leads", included: true },
      { text: "Unlimited WhatsApp outreach", included: true },
      { text: "Unlimited email outreach", included: true },
      { text: "AI scoring + AI message generation", included: true },
      { text: "Advanced analytics + custom reports", included: true },
      { text: "All 10 cities + custom zones", included: true },
      { text: "HubSpot + Salesforce sync", included: true },
      { text: "AI document verification suite", included: true },
      { text: "Agent partnership portal + white-label", included: true },
      { text: "Multi-city parallel campaigns", included: true },
      { text: "Dedicated account manager + SLA", included: true },
    ],
    highlight: null,
  },
];

const addons = [
  { name: "Additional LPI Certificates", price: "₹2,500 each" },
  { name: "LPI Annual Registry Subscription", price: "₹12,000/year/parcel" },
  { name: "Agent LPI License (partner price)", price: "₹0 (waived for partners)" },
  { name: "Apify Scraping Proxy (enhanced)", price: "₹3,999/month" },
  { name: "Make.com Automation Setup", price: "₹9,999 one-time" },
  { name: "n8n Self-Hosted Setup", price: "₹14,999 one-time" },
  { name: "Custom City Zone Mapping", price: "₹24,999 per city" },
  { name: "NRI Campaign Package", price: "₹49,999/campaign" },
];

const faqs = [
  { q: "Is the LPI Certificate legally valid in India?", a: "LPI Certificates are issued by ICP3A as satellite-precision supporting documentation. They are used alongside standard government documents (Khata, Sale Deed) for RERA compliance, bank loan submissions, and property valuation. They are not a replacement for government title deeds." },
  { q: "How quickly does the first outreach fire?", a: "Within 2 minutes of a lead being created or imported. The Celery worker picks up the task, Claude AI scores the lead, and Twilio fires the WhatsApp message automatically — no human intervention required." },
  { q: "Can I import my existing leads?", a: "Yes. The import script supports CSV, Excel (.xlsx), and JSON with automatic column name detection — handles 40+ naming variants like 'Name', 'Owner', 'Seller', 'Phone', 'Mobile', etc." },
  { q: "What happens if a lead doesn't respond?", a: "Automated follow-ups fire on Day 3, Day 7, and Day 14. If there's still no response, the lead is moved to a cold list and re-engaged quarterly. All follow-up scheduling is handled by Celery — zero manual work." },
  { q: "Is the LPI Certificate mandatory for deal approval?", a: "Yes, by design. The ICP3A pipeline will not advance a lead past 'under_verification' without a valid LPI Certificate. This is our core quality gate — it ensures every property we acquire has satellite-grade boundary certification." },
  { q: "What cities are covered?", a: "10 cities across 3 tiers: Delhi NCR, Mumbai, Bengaluru (Tier 1); Hyderabad, Chennai, Kolkata, Pune (Tier 2); Ahmedabad, Goa, Kochi (Tier 3). Enterprise customers can add custom zones." },
];

export default function PricingPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* HERO */}
        <section className="gradient-hero" style={{ paddingTop: 128, paddingBottom: 72 }}>
          <div className="max-w-4xl mx-auto px-6 text-center">
            <p className="section-label mb-4" style={{ color: "#F59E0B" }}>PRICING</p>
            <h1 style={{ color: "white", fontSize: "clamp(2rem,5vw,3.5rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 16, lineHeight: 1.1 }}>
              Transparent pricing.<br />Unlimited acquisitions.
            </h1>
            <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "1.05rem", lineHeight: 1.75 }}>
              All plans include Claude AI scoring, WhatsApp outreach, and the ICP3A dashboard. No hidden fees.
            </p>
          </div>
        </section>

        {/* PLANS */}
        <section style={{ padding: "80px 0", background: "#F8FAFC" }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
              {plans.map(p => (
                <div key={p.name} className={`pricing-card ${p.featured ? "featured" : ""}`}>
                  <div style={{ marginBottom: 6 }}>
                    <span style={{
                      fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.12em",
                      background: p.featured ? "#F59E0B22" : "#F1F5F9",
                      color: p.featured ? "#F59E0B" : "#64748B",
                      border: p.featured ? "1px solid #F59E0B44" : "none",
                      borderRadius: 4, padding: "3px 8px"
                    }}>{p.tag}</span>
                  </div>
                  <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: p.featured ? "white" : "#0F172A", margin: "10px 0 6px" }}>{p.name}</h2>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 4, marginBottom: 12 }}>
                    <span style={{ fontSize: "2.25rem", fontWeight: 800, color: p.featured ? "#F59E0B" : p.color, fontFamily: "Space Grotesk,sans-serif" }}>{p.price}</span>
                    <span style={{ color: p.featured ? "rgba(255,255,255,0.45)" : "#94A3B8", fontSize: "0.88rem" }}>{p.period}</span>
                  </div>
                  {p.highlight && (
                    <div style={{ background: "#F59E0B22", border: "1px solid #F59E0B44", color: "#F59E0B", borderRadius: 6, padding: "4px 12px", fontSize: "0.75rem", fontWeight: 600, display: "inline-block", marginBottom: 12 }}>{p.highlight}</div>
                  )}
                  <p style={{ color: p.featured ? "rgba(255,255,255,0.55)" : "#64748B", fontSize: "0.86rem", lineHeight: 1.65, marginBottom: 24 }}>{p.desc}</p>

                  <Link href={p.href} className={p.featured ? "btn-gold" : "btn-primary"} style={{ width: "100%", justifyContent: "center", marginBottom: 28, background: p.featured ? "linear-gradient(90deg,#F59E0B,#FBBF24)" : undefined }}>
                    {p.cta} →
                  </Link>

                  <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
                    {p.features.map(f => (
                      <li key={f.text} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                        <span style={{ flexShrink: 0, marginTop: 1, fontSize: "0.9rem", color: f.included ? (p.featured ? "#F59E0B" : "#10B981") : (p.featured ? "rgba(255,255,255,0.2)" : "#CBD5E1") }}>
                          {f.included ? "✓" : "✕"}
                        </span>
                        <span style={{ fontSize: "0.84rem", color: f.included ? (p.featured ? "rgba(255,255,255,0.85)" : "#334155") : (p.featured ? "rgba(255,255,255,0.3)" : "#94A3B8"), textDecoration: f.included ? "none" : "none" }}>
                          {f.text}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ADD-ONS */}
        <section style={{ padding: "80px 0", background: "white" }}>
          <div className="max-w-4xl mx-auto px-6">
            <div className="text-center mb-12">
              <p className="section-label mb-3">ADD-ONS</p>
              <h2 style={{ fontSize: "clamp(1.5rem,3vw,2.25rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>A la carte options</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {addons.map(a => (
                <div key={a.name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderRadius: 10, border: "1px solid #E2E8F0", background: "#F8FAFC" }}>
                  <span style={{ color: "#334155", fontSize: "0.88rem", fontWeight: 500 }}>{a.name}</span>
                  <span style={{ color: "#1D4ED8", fontWeight: 700, fontSize: "0.88rem", whiteSpace: "nowrap", marginLeft: 16 }}>{a.price}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section style={{ padding: "80px 0", background: "#F8FAFC" }}>
          <div className="max-w-3xl mx-auto px-6">
            <div className="text-center mb-12">
              <p className="section-label mb-3">FAQ</p>
              <h2 style={{ fontSize: "clamp(1.5rem,3vw,2.25rem)", fontWeight: 700, color: "#060D1F", letterSpacing: "-0.02em" }}>Common questions</h2>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {faqs.map(f => (
                <div key={f.q} style={{ borderRadius: 12, border: "1px solid #E2E8F0", padding: "22px 24px", background: "white" }}>
                  <h3 style={{ fontWeight: 700, color: "#0F172A", fontSize: "0.95rem", marginBottom: 10 }}>{f.q}</h3>
                  <p style={{ color: "#64748B", fontSize: "0.88rem", lineHeight: 1.75, margin: 0 }}>{f.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section style={{ background: "linear-gradient(135deg,#060D1F,#0C1A3A)", padding: "72px 0" }}>
          <div className="max-w-2xl mx-auto px-6 text-center">
            <h2 style={{ color: "white", fontSize: "clamp(1.6rem,4vw,2.5rem)", fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 14 }}>Questions? Talk to Philip George.</h2>
            <p style={{ color: "rgba(255,255,255,0.5)", marginBottom: 36 }}>Our team will help you choose the right plan and get you set up in under 2 hours.</p>
            <Link href="/contact" className="btn-gold" style={{ fontSize: "1rem", padding: "14px 36px" }}>Book a Call →</Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
