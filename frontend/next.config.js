/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",  // Matches any request starting with /api/
        destination: `http://localhost:6001/api/:path*`,  // Forwards to backend using dynamic URL
      },
    ];
  },
  // Other Next.js configurations can go here
  
  // Expose environment variables to the browser
  env: {
    NEXT_PUBLIC_API_BASE_URL: 'http://localhost:6001/api',
    // Keep existing publicRuntimeConfig for now, or migrate them here too
    NEXT_PUBLIC_APP_HOST: 'http://localhost',
    NEXT_PUBLIC_BACKEND_PORT: '6001',
    NEXT_PUBLIC_LOGIN_URL_SUFFIX: 'api/auth/login',
    NEXT_PUBLIC_LOGOUT_URL_SUFFIX: 'api/auth/logout',
    NEXT_PUBLIC_SESSION_URL_SUFFIX: 'api/session',
  },

  publicRuntimeConfig: {
    // Values here are available on both server and client.
    // Consider migrating fully to `env` for client-side vars.
    appHost: 'http://localhost',
    backendPort: 6001,
    loginUrlSuffix: 'api/auth/login',
    logoutUrlSuffix: 'api/auth/logout',
    sessionUrlSuffix: 'api/session',
  },
};

module.exports = nextConfig; 
