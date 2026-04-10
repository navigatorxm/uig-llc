import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const contactOptions = [
  { icon: "💬", title: "WhatsApp Philip George", desc: "Fastest response. Direct line to our Head of Asia Pacific. Replies within 2 hours during IST business hours.", action: "Chat on WhatsApp →", href: "https://wa.me/919999999999", color: "#25D366" },
  { icon: "📧", title: "Email the Team", desc: "For formal enquiries, document submissions, and partnership proposals. Response within 24 hours.", action: "Send Email →", href: "mailto:philip.george@icp3a.in", color: "#1D4ED8" },
  { icon: "📞", title: "Book a Call", desc: "Schedule a 30-minute discovery call with Philip George. Available Mon–Sat, 9AM–7PM IST.", action: "Book via Calendly →", href: "#", color: "#8B5CF6" },
];

const offices = [
  { city: "Delhi NCR (HQ)", address: "Aerocity Business Hub, IGI Airport Zone\nNew Delhi — 110037", phone: "+91 99999 99999", email: "delhi@icp3a.in" },
  { city: "Mumbai", address: "BKC Tower, Bandra Kurla Complex\nMumbai — 400051", phone: "+91 99999 99998", email: "mumbai@icp3a.in" },
  { city: "Bengaluru", address: "Devanahalli Business Park\nBengaluru — 562110", phone: "+91 99999 99997", email: "bengaluru@icp3a.in" },
];

const enquiryTypes = [
  "Property Acquisition Enquiry",
  "LPI Certificate Application",
  "Agent Partnership Application",
  "NRI Investment Enquiry",
  "Enterprise / Bulk Acquisition",
  "Investor / Funding Discussion",
  "Press / Media",
  "Other",
];

export default function ContactPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* HERO */}
        <section className="gradient-hero" style={{ paddingTop: 128, paddingBottom: 72 }}>
          <div className="max-w-4xl mx-auto px-6 text-center">
            <p className="section-label mb-4" style={{ color: "#F59E0B" }}>CONTACT</p>
            <h1 style={{ color: "white", fontSize: "clamp(2rem,5vw,3.5rem)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 16, lineHeight: 1.1 }}>
              Talk to Philip George
            </h1>
            <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "1.05rem", lineHeight: 1.75 }}>
              Property Acquisition Manager · Head of Asia Pacific, ICP3A<br />
              philip.george@icp3a.in · Delhi NCR
            </p>
          </div>
        </section>

        {/* CONTACT OPTIONS */}
        <section style={{ padding: "72px 0", background: "white" }}>
          <div className="max-w-5xl mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
              {contactOptions.map(c => (
                <div key={c.title} className="card-glow" style={{ borderRadius: 16, padding: 28, border: "1px solid #E2E8F0", textAlign: "center" }}>
                  <div style={{ fontSize: "2.5rem", marginBottom: 16 }}>{c.icon}</div>
                  <h3 style={{ fontWeight: 700, color: "#0F172A", fontSize: "1rem", marginBottom: 10 }}>{c.title}</h3>
                  <p style={{ color: "#64748B", fontSize: "0.86rem", lineHeight: 1.7, marginBottom: 20 }}>{c.desc}</p>
                  <a href={c.href} style={{ color: c.color, fontWeight: 700, fontSize: "0.88rem", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 6 }}>
                    {c.action}
                  </a>
                </div>
              ))}
            </div>

            {/* ENQUIRY FORM */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
              <div>
                <h2 style={{ fontSize: "1.75rem", fontWeight: 800, color: "#060D1F", letterSpacing: "-0.02em", marginBottom: 12 }}>Send an enquiry</h2>
                <p style={{ color: "#64748B", lineHeight: 1.75, fontSize: "0.92rem", marginBottom: 32 }}>Fill in the form and Philip George's team will respond within 24 hours. For urgent matters, WhatsApp is fastest.</p>

                <form style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  {[
                    { label: "Full Name", type: "text", placeholder: "Your full name" },
                    { label: "Phone / WhatsApp", type: "tel", placeholder: "+91 XXXXX XXXXX" },
                    { label: "Email Address", type: "email", placeholder: "you@example.com" },
                    { label: "Property Address / Area", type: "text", placeholder: "e.g. Aerocity, New Delhi" },
                  ].map(f => (
                    <div key={f.label}>
                      <label style={{ display: "block", color: "#374151", fontSize: "0.84rem", fontWeight: 600, marginBottom: 6 }}>{f.label}</label>
                      <input type={f.type} placeholder={f.placeholder} style={{ width: "100%", padding: "11px 14px", border: "1.5px solid #E2E8F0", borderRadius: 8, fontSize: "0.9rem", color: "#0F172A", outline: "none", background: "white" }} />
                    </div>
                  ))}

                  <div>
                    <label style={{ display: "block", color: "#374151", fontSize: "0.84rem", fontWeight: 600, marginBottom: 6 }}>Enquiry Type</label>
                    <select style={{ width: "100%", padding: "11px 14px", border: "1.5px solid #E2E8F0", borderRadius: 8, fontSize: "0.9rem", color: "#0F172A", background: "white", outline: "none" }}>
                      <option value="">Select enquiry type</option>
                      {enquiryTypes.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", color: "#374151", fontSize: "0.84rem", fontWeight: 600, marginBottom: 6 }}>Message</label>
                    <textarea placeholder="Tell us about your property, investment goal, or question..." rows={4} style={{ width: "100%", padding: "11px 14px", border: "1.5px solid #E2E8F0", borderRadius: 8, fontSize: "0.9rem", color: "#0F172A", outline: "none", resize: "vertical", background: "white" }} />
                  </div>

                  <button type="submit" className="btn-gold" style={{ fontSize: "0.95rem", padding: "13px 0", justifyContent: "center", width: "100%" }}>
                    Send Enquiry →
                  </button>

                  <p style={{ color: "#94A3B8", fontSize: "0.76rem", textAlign: "center" }}>
                    By submitting, you agree to be contacted by Philip George / ICP3A regarding your enquiry.
                  </p>
                </form>
              </div>

              {/* OFFICES */}
              <div>
                <h2 style={{ fontSize: "1.75rem", fontWeight: 800, color: "#060D1F", letterSpacing: "-0.02em", marginBottom: 12 }}>Office locations</h2>
                <p style={{ color: "#64748B", lineHeight: 1.75, fontSize: "0.92rem", marginBottom: 32 }}>Visit us at any of our airport-zone offices, or connect with our city teams directly.</p>

                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  {offices.map(o => (
                    <div key={o.city} style={{ padding: "20px 22px", borderRadius: 12, border: "1px solid #E2E8F0", background: "#F8FAFC" }}>
                      <h3 style={{ fontWeight: 700, color: "#0F172A", fontSize: "0.95rem", marginBottom: 8 }}>{o.city}</h3>
                      <p style={{ color: "#64748B", fontSize: "0.84rem", lineHeight: 1.7, marginBottom: 10, whiteSpace: "pre-line" }}>{o.address}</p>
                      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                        <a href={`tel:${o.phone}`} style={{ color: "#1D4ED8", fontSize: "0.82rem", fontWeight: 600, textDecoration: "none" }}>{o.phone}</a>
                        <a href={`mailto:${o.email}`} style={{ color: "#1D4ED8", fontSize: "0.82rem", fontWeight: 600, textDecoration: "none" }}>{o.email}</a>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ marginTop: 24, padding: "20px 22px", borderRadius: 12, background: "#060D1F", border: "1px solid rgba(255,255,255,0.08)" }}>
                  <div className="lpi-badge inline-block px-3 py-1 rounded-full mb-3">GLOBAL HQ</div>
                  <h3 style={{ color: "white", fontWeight: 700, fontSize: "0.95rem", marginBottom: 4 }}>United Investing Group LLC</h3>
                  <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.82rem", lineHeight: 1.65 }}>
                    ICP3A is the India operations division of United Investing Group LLC, a private satellite earth-mapping company operating globally across 40+ countries.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
