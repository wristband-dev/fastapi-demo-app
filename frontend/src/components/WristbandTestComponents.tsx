/**
 * WristbandTestComponents
 * 
 * This component provides a UI for testing the Wristband authentication system.
 * It includes functionality to test cookie decryption and display responses.
 */
import { useState } from "react";
import frontendApiClient from "@/client/frontend-api-client";
import { handleApiError } from "@/utils/ApiError";

export default function WristbandTestComponents() {
  const [response, setResponse] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Tests the cookie decryption by making an API call to the backend
   */
  const handleTestDecryptCookie = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Using our API client with CSRF protection instead of fetch
      const res = await frontendApiClient.get('/auth/test_decrypt_cookie');
      setResponse(JSON.stringify(res.data));
    } catch (error) {
      // Use our standardized error handling
      const apiError = handleApiError(error);
      console.error("Error:", apiError);
      setError(apiError.message);
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Formats response data as pretty JSON if possible
   */
  const formatResponse = (responseData: string) => {
    try {
      // Try to parse as JSON first
      const parsed = JSON.parse(responseData);
      return JSON.stringify(parsed, null, 2);
    } catch (e) {
      // If not valid JSON, just show as string
      return responseData;
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      <button
        onClick={handleTestDecryptCookie}
        disabled={isLoading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
      >
        {isLoading ? "Testing..." : "Test Decrypt Cookie"}
      </button>
     
      {error && (
        <div className="mt-4 rounded border border-red-300 bg-red-50 dark:bg-red-900 dark:border-red-700 p-2">
          <p className="text-red-600 dark:text-red-300 text-sm">{error}</p>
        </div>
      )}

      {response && (
        <div className="mt-4 rounded border border-gray-300 dark:border-gray-700">
          <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
            <p className="font-bold text-sm">Response:</p>
          </div>
          <div className="p-2 max-h-60 overflow-auto">
            <pre className="text-xs whitespace-pre-wrap break-all">
              {typeof response === 'string' ? formatResponse(response) : JSON.stringify(response, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
} 