/**
 * Authentication Configuration
 * 
 * This module provides centralized configuration for authentication endpoints.
 * It pulls values from Next.js runtime configuration and constructs the necessary URLs
 * for login, logout, and session management.
 */
import getConfig from 'next/config';

const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} };

// Extract key values from publicRuntimeConfig
// Provide defaults if values might be undefined
const appHost = publicRuntimeConfig.appHost || 'http://localhost';
const backendPort = publicRuntimeConfig.backendPort || '8001';
const loginUrlSuffix = publicRuntimeConfig.loginUrlSuffix || 'api/auth/login';
const logoutUrlSuffix = publicRuntimeConfig.logoutUrlSuffix || 'api/auth/logout';
const sessionUrlSuffix = publicRuntimeConfig.sessionUrlSuffix || 'api/auth/session';

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