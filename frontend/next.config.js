/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for deployment
  output: 'export',
  trailingSlash: true,
  distDir: 'out',

  images: {
    domains: ['localhost', 'playbookwiz.com'],
    formats: ['image/webp', 'image/avif'],
    unoptimized: true, // Required for static export
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' http://localhost:8000 https://api.openai.com https://api.anthropic.com https://*.supabase.co wss://*.supabase.co; font-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none';",
          },
        ],
      },
    ];
  },
  webpack: (config, { isServer }) => {
    // Handle PDF.js worker
    config.resolve.alias.canvas = false;
    config.resolve.alias.encoding = false;

    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },
};

module.exports = nextConfig;
