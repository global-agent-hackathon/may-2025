// Load EventEmitter configuration early to prevent max listeners warning
try {
  require('./src/lib/eventEmitter');
} catch (error) {
  console.log('Warning: EventEmitter config could not be loaded, proceeding without it');
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // External packages that can be used by server components
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Add transpilePackages for Clerk if needed
  transpilePackages: ['@clerk/nextjs'],
  // Ensure API endpoints are always processed as Server-Side
  eslint: {
    // Ignore ESLint during builds for faster development
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig; 