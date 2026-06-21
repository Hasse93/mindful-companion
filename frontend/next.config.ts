import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow accessing the dev server from the local network (e.g. 192.168.x.x)
  // so HMR and font loading work when visiting the app from another device
  // or via the network IP in development.
  allowedDevOrigins: ["192.168.1.113"],
};

export default nextConfig;
