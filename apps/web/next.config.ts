import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  allowedDevOrigins: ['*.e2b.app', 'localhost', '127.0.0.1'],
  async redirects() {
    return [
      {
        source: '/admin',
        destination: '/admin/reports',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
