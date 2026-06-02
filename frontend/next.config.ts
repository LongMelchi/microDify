import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // Allow cross-origin requests in dev (e.g. from Docker/WSL network)
  allowedDevOrigins: ["172.28.224.1", "localhost", "127.0.0.1"],

  // API requests proxied to the FastAPI backend during development.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/:path*`,
      },
    ];
  },
};

export default nextConfig;
