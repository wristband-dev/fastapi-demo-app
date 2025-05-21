const path = require('path');
const fs = require('fs');
const yaml = require('yaml');

// Path to config.yml, assuming next.config.js is in the 'frontend' directory
// and config.yml is in the parent directory of 'frontend'
const configPath = path.join(__dirname, '../config.yml');
let appConfig = {};

try {
  const fileContents = fs.readFileSync(configPath, 'utf8');
  appConfig = yaml.parse(fileContents) || {};
} catch (error) {
  console.error('Error reading or parsing config.yml:', error);
  // Provide default values or handle the error as appropriate
}

// Construct the backend URL from the loaded config
const appHost = appConfig.app?.host;
const backendPort = appConfig.backend?.port; // Default to 6001 if not found
const backendUrl = `${appHost}:${backendPort}`;
const apiBaseUrl = `${backendUrl}/api`; // For client-side use

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true, // Or your existing config
  async rewrites() {
    return [
      {
        source: "/api/:path*",  // Matches any request starting with /api/
        destination: `${backendUrl}/api/:path*`,  // Forwards to backend using dynamic URL
      },
    ];
  },
  // Other Next.js configurations can go here
  
  // Expose environment variables to the browser
  env: {
    NEXT_PUBLIC_API_BASE_URL: apiBaseUrl,
    // Keep existing publicRuntimeConfig for now, or migrate them here too
    NEXT_PUBLIC_APP_HOST: appConfig.app?.host,
    NEXT_PUBLIC_BACKEND_PORT: appConfig.backend?.port?.toString(),
    NEXT_PUBLIC_LOGIN_URL_SUFFIX: appConfig.backend?.login_url_suffix,
    NEXT_PUBLIC_LOGOUT_URL_SUFFIX: appConfig.backend?.logout_url_suffix,
    NEXT_PUBLIC_SESSION_URL_SUFFIX: appConfig.backend?.session_url_suffix,
  },

  publicRuntimeConfig: {
    // Values here are available on both server and client.
    // Consider migrating fully to `env` for client-side vars.
    appHost: appConfig.app?.host,
    backendPort: appConfig.backend?.port,
    loginUrlSuffix: appConfig.backend?.login_url_suffix,
    logoutUrlSuffix: appConfig.backend?.logout_url_suffix,
    sessionUrlSuffix: appConfig.backend?.session_url_suffix,
  },
  // serverRuntimeConfig could be used for configs only needed server-side
  // serverRuntimeConfig: {
  //   appConfig: appConfig, // The whole config for server-side use
  // },
};

module.exports = nextConfig; 