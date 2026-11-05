import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  output: "standalone",
  // officeparser uses runtime module loading for its PDF/OCR dependencies.
  serverExternalPackages: ["officeparser"],
};
export default nextConfig;
