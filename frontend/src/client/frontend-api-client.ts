/**
 * This module configures and exports an Axios instance for making API requests to the backend.
 * It automatically handles common headers and base URL configuration from Next.js runtime config.
 * Includes CSRF protection and unauthorized access handling.
 */
import axios from 'axios';
import { redirectToLogin } from '@wristband/react-client-auth';

const JSON_MEDIA_TYPE = 'application/json;charset=UTF-8';

const frontendApiClient = axios.create({
  baseURL: `/api`,
  headers: { 'Content-Type': JSON_MEDIA_TYPE, Accept: JSON_MEDIA_TYPE },
  /* CSRF_TOUCHPOINT */
  xsrfCookieName: 'CSRF-TOKEN',
  xsrfHeaderName: 'X-CSRF-TOKEN',
  withCredentials: true,
});

// Add an unauthorized access interceptor to handle 401 or 403 responses
const unauthorizedAccessInterceptor = (error: unknown) => {
  if (axios.isAxiosError(error) && [401, 403].includes(error.response?.status!)) {
    redirectToLogin('/api/auth/login');
  }
  return Promise.reject(error);
};
frontendApiClient.interceptors.response.use((response) => response, unauthorizedAccessInterceptor);

export default frontendApiClient;
