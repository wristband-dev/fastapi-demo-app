/**
 * Frontend API Service
 * 
 * This service provides methods for interacting with the backend API.
 * It uses the frontendApiClient to make requests and handles common API patterns.
 */
import frontendApiClient from "@/client/frontend-api-client";
import { handleApiError } from "@/utils/ApiError";

/**
 * Fetches the current user session information
 * @returns {Promise<any>} Session data from the backend
 */
async function getSession() {
  try {
    // The API client already has withCredentials set to true
    // and includes CSRF protection
    const response = await frontendApiClient.get(`/session`, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        Pragma: 'no-cache',
        Expires: '0',
      }
    });

    return response.data;
  } catch (error) {
    // Use our standardized error handling
    throw handleApiError(error);
  }
}

/**
 * Makes a test API call to the backend
 * Example of using our API client
 */
async function testApiCall() {
  try {
    const response = await frontendApiClient.get('/test-endpoint');
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

export const frontendApiService = {
  getSession,
  testApiCall,
};
