import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "VU Academic Advisor", description: "Academic guidance for Vidyashilp University students." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}