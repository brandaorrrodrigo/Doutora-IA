/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://api.doutoraia.com',
  },
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
}

module.exports = nextConfig
