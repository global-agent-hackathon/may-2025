import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // for loading the google user profile image in Next JS
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
