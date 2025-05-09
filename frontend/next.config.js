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

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true, // Or your existing config
  async rewrites() {
    return [
      {
        source: "/api/:path*",  // Matches any request starting with /api/
        destination: "http://localhost:8080/api/:path*",  // Forwards to backend
      },
    ];
  },
  // Other Next.js configurations can go here
  
  publicRuntimeConfig: {
    // Make config values available to the client
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