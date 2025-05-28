/**
 * Frontend API Client
 * 
 * This module configures and exports an Axios instance for making API requests to the backend.
 * It automatically handles common headers and base URL configuration from Next.js runtime config.
 * Includes CSRF protection and unauthorized access handling.
 */
import axios from 'axios';
import getConfig from 'next/config';
import { loginUrl } from '@/lib/authConfig';
import { 
  JSON_MEDIA_TYPE, 
  CSRF_TOKEN_COOKIE_NAME, 
  CSRF_TOKEN_HEADER_NAME 
} from '@/utils/contstants';

const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} };

// Extract key values from publicRuntimeConfig
// Provide defaults if values might be undefined at build time but available at runtime
const appHost = publicRuntimeConfig.appHost || 'http://localhost:3001'; // Default, if not set
const backendPort = publicRuntimeConfig.backendPort || 8000; // Default, if not set

const defaultOptions = {
  // Set up baseURL based on the app host and backend port from publicRuntimeConfig
  baseURL: `${appHost}:${backendPort}/api`,
  headers: { 'Content-Type': JSON_MEDIA_TYPE, Accept: JSON_MEDIA_TYPE },
  // CSRF protection configuration
  xsrfCookieName: CSRF_TOKEN_COOKIE_NAME,
  xsrfHeaderName: CSRF_TOKEN_HEADER_NAME,
  withCredentials: true, // Include cookies in requests (needed for both authentication and CSRF)
};

const frontendApiClient = axios.create(defaultOptions);

// Unauthorized access interceptor to handle 401 or 403 responses
const unauthorizedAccessInterceptor = (error: unknown) => {
  if (axios.isAxiosError(error) && (error.response?.status === 401 || error.response?.status === 403)) {
    // Redirect to login page
    window.location.href = loginUrl;
    return Promise.reject(error);
  }
  
  return Promise.reject(error);
};

// Add the interceptor to the client
frontendApiClient.interceptors.response.use(
  (response) => response, // Pass successful responses through
  unauthorizedAccessInterceptor // Handle errors
);

export default frontendApiClient;