const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://127.0.0.1:8088',
  },
  async rewrites() {
    const apiBase = process.env.API_BASE_URL || 'http://127.0.0.1:8088';
    return [
      {
        source: '/api/consultation',
        destination: `${apiBase}/consultation`,
      },
      {
        source: '/api/rights/checklist',
        destination: `${apiBase}/rights/checklist`,
      },
      {
        source: '/api/evidence/checklist',
        destination: `${apiBase}/evidence/checklist`,
      },
      {
        source: '/api/consultations/recent',
        destination: `${apiBase}/consultations/recent`,
      },
      {
        source: '/api/consultations/:consultation_id/lawsuit',
        destination: `${apiBase}/consultations/:consultation_id/lawsuit`,
      },
      {
        source: '/api/consultations/:consultation_id/lawsuit/fields',
        destination: `${apiBase}/consultations/:consultation_id/lawsuit/fields`,
      },
      {
        source: '/api/lawsuit/generate-from-form',
        destination: `${apiBase}/lawsuit/generate-from-form`,
      },
      {
        source: '/api/lawsuit/template-fields',
        destination: `${apiBase}/lawsuit/template-fields`,
      },
      {
        source: '/api/consultations/:consultation_id',
        destination: `${apiBase}/consultations/:consultation_id`,
      },
      {
        source: '/api/calculator/:path*',
        destination: `${apiBase}/calculator/:path*`,
      },
      {
        source: '/api/health',
        destination: `${apiBase}/health`,
      },
    ];
  },
};

export default nextConfig;
