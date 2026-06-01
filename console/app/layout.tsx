import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Service Console",
  description: "Local development console for ML and agent services",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
