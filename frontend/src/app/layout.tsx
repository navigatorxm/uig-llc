import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ICP3A — Integrated Certified Property Precision Acquisition & Analytics",
  description: "India's first satellite-grade property certification and acquisition platform. LPI certified. 28 airports. All major cities.",
  keywords: "LPI certificate, property acquisition, India real estate, airport zone property, ICP3A",
  openGraph: {
    title: "ICP3A — Every Parcel. Certified. Acquired.",
    description: "Satellite-grade LPI certification for every 10×10m land parcel. Automated property acquisition across all Indian airport zones.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
