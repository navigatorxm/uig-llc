import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UIG Acquisition Pipeline",
  description: "United Investing Group LLC — Property Acquisition Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
