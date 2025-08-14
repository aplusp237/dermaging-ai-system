/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
    dangerouslyAllowSVG: true,
  },
  // Configure rewrites for local AI model endpoints
  async rewrites() {
    return [
      {
        source: '/api/llava/:path*',
        destination: 'http://localhost:8001/:path*', // Local LLaVA endpoint
      },
      {
        source: '/api/medgemma/:path*',
        destination: 'http://localhost:8002/:path*', // Local MedGemma endpoint
      },
    ]
  },
}

module.exports = nextConfig 