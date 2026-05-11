import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

// Content Security Policy directives
const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' blob: data: https:;
  font-src 'self' data:;
  connect-src 'self' ws: wss: http://localhost:* https://localhost:*;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
`.replace(/\n/g, " ").trim();

const securityHeaders = [
  {
    key: "Content-Security-Policy",
    value: ContentSecurityPolicy,
  },
  {
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
  {
    key: "X-Frame-Options",
    value: "DENY",
  },
  {
    key: "X-XSS-Protection",
    value: "1; mode=block",
  },
  {
    key: "Referrer-Policy",
    value: "strict-origin-when-cross-origin",
  },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
];

const isCloudflare = process.env.IS_CLOUDFLARE === "true";

const nextConfig: NextConfig = {
  output: isCloudflare ? "export" : "standalone",
  images: {
    unoptimized: isCloudflare,
  },
  typescript: {
    // Disable type checking on build for Cloudflare export compatibility
    ignoreBuildErrors: isCloudflare,
  },
  eslint: {
    // Disable linting on build for Cloudflare export compatibility
    ignoreDuringBuilds: isCloudflare,
  },
  // Security headers
  async headers() {
    // Headers only work in non-export mode
    if (isCloudflare) return [];
    
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },

  // Environment variables available on the server side only
  serverRuntimeConfig: {
    apiUrl: process.env.BACKEND_URL || "http://localhost:8000",
  },

  // Environment variables available on both server and client
  publicRuntimeConfig: {
    appName: "shb_chatbot",
  },
};

export default withNextIntl(nextConfig);
