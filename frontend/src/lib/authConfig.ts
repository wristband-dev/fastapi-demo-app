import config from './config';

// Extract key values from config
const appHost = config.app.host;
const backendPort = config.backend.port;
const loginUrlSuffix = config.backend.login_url_suffix;
const logoutUrlSuffix = config.backend.logout_url_suffix;
const sessionUrlSuffix = config.backend.session_url_suffix;

// Build auth URLs
export const loginUrl = `${appHost}:${backendPort}/${loginUrlSuffix}`;
export const logoutUrl = `${appHost}:${backendPort}/${logoutUrlSuffix}`;
export const sessionUrl = `${appHost}:${backendPort}/${sessionUrlSuffix}`;

export default {
  loginUrl,
  logoutUrl,
  sessionUrl
}; 