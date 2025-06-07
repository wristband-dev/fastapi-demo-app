/**
 * Frontend API Client
 * 
 * This module configures and exports an Axios instance for making API requests to the backend.
 * It automatically handles common headers and base URL configuration from Next.js runtime config.
 * Includes CSRF protection and unauthorized access handling.
 */
import axios from 'axios';
import getConfig from 'next/config';
import { redirectToLogin } from '@wristband/react-client-auth';

import { loginUrl } from '@/lib/authConfig';

const JSON_MEDIA_TYPE = 'application/json;charset=UTF-8';
const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} };
const { appHost, backendPort } = publicRuntimeConfig;

const defaultOptions = {
  // Set up baseURL based on the app host and backend port from publicRuntimeConfig
  baseURL: `${appHost}:${backendPort}/api`,
  headers: { 'Content-Type': JSON_MEDIA_TYPE, Accept: JSON_MEDIA_TYPE },
  // CSRF protection configuration
  xsrfCookieName: 'CSRF-TOKEN',
  xsrfHeaderName: 'X-CSRF-TOKEN',
  withCredentials: true, // Include cookies in requests (needed for both authentication and CSRF)
};

const frontendApiClient = axios.create(defaultOptions);

// Unauthorized access interceptor to handle 401 or 403 responses
const unauthorizedAccessInterceptor = (error: unknown) => {
  if (axios.isAxiosError(error) && [401, 403].includes(error.response?.status!)) {
    redirectToLogin(loginUrl);
    return Promise.reject(error);
  }
  
  return Promise.reject(error);
};

// Add the interceptor to the client
frontendApiClient.interceptors.response.use((response) => response, unauthorizedAccessInterceptor);

export default frontendApiClient;
