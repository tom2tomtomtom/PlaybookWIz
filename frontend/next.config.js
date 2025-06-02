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
  // Headers don't work with static export, so we'll handle CSP differently
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
