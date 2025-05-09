import getConfig from 'next/config';

const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} };

// Extract key values from publicRuntimeConfig
// Provide defaults if values might be undefined
const appHost = publicRuntimeConfig.appHost;
const backendPort = publicRuntimeConfig.backendPort;
const loginUrlSuffix = publicRuntimeConfig.loginUrlSuffix;
const logoutUrlSuffix = publicRuntimeConfig.logoutUrlSuffix;
const sessionUrlSuffix = publicRuntimeConfig.sessionUrlSuffix;

// Build auth URLs
export const loginUrl = `${appHost}:${backendPort}/${loginUrlSuffix}`;
export const logoutUrl = `${appHost}:${backendPort}/${logoutUrlSuffix}`;
export const sessionUrl = `${appHost}:${backendPort}/${sessionUrlSuffix}`;

const authConfig = {
  loginUrl,
  logoutUrl,
  sessionUrl
};

export default authConfig; 