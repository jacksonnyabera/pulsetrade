import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["cheddar-reopen-washcloth.ngrok-free.dev"],
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://backend:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;