import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",  // Matches any request starting with /api/
        destination: "http://localhost:8080/api/:path*",  // Forwards to backend
      },
    ];
  },
};

export default nextConfig;