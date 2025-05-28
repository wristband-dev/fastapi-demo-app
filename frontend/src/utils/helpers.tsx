/**
 * Helper Utilities
 * 
 * This module provides reusable helper functions for the application.
 */
import { useState } from 'react';
import { handleApiError, ApiError } from './ApiError';

/**
 * Helper hook for making API calls with consistent loading and error handling
 * @param apiCall The API function to call
 * @returns Object with data, loading state, error state, and execute function
 */
export function useApiCall<T>(
  apiCall: (...args: any[]) => Promise<T>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);

  /**
   * Execute the API call with arguments
   */
  const execute = async (...args: any[]) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall(...args);
      setData(result);
      return result;
    } catch (err) {
      const apiError = err instanceof ApiError ? err : handleApiError(err);
      setError(apiError);
      console.error('API call failed:', apiError);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute };
}

/**
 * Formats a date string into a localized format
 * @param dateString The date string to format
 * @returns Formatted date string
 */
export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString;
  }
};