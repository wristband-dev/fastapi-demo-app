/**
 * API Error Utilities
 * 
 * This module provides utility functions for handling API errors consistently across the application.
 */
import axios from 'axios';
import { loginUrl } from '@/lib/authConfig';

/**
 * Custom API error class to standardize error handling
 */
export class ApiError extends Error {
  status?: number;
  data?: any;

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Handles common API error scenarios in a standardized way
 * @param error The error caught from an API call
 * @param customErrorHandler Optional custom handler for specific error scenarios
 * @returns A standardized ApiError object
 */
export const handleApiError = (error: unknown, customErrorHandler?: (error: unknown) => void): ApiError => {
  // Allow custom handling if provided
  if (customErrorHandler) {
    customErrorHandler(error);
  }

  // Handle Axios errors
  if (axios.isAxiosError(error)) {
    // Handle authentication errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Redirect to login page
      window.location.href = loginUrl;
      return new ApiError('Authentication required', error.response.status, error.response.data);
    }

    // Return a standardized error for other API errors
    return new ApiError(
      error.response?.data?.message || error.message || 'An error occurred with the API',
      error.response?.status,
      error.response?.data
    );
  }

  // Handle other types of errors
  return new ApiError(error instanceof Error ? error.message : 'An unexpected error occurred');
};