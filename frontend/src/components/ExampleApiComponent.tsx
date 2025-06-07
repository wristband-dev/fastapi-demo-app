/**
 * Example API Component
 * 
 * This component demonstrates how to properly use the API client with CSRF protection
 * and standardized error handling.
 */
import { useState } from 'react';
import frontendApiClient from '@/client/frontend-api-client';
import { frontendApiService } from '@/services/frontend-api-service';
import { useApiCall } from '@/utils/helpers';

export default function ExampleApiComponent() {
  // Example 1: Using the API service
  const [serviceResponse, setServiceResponse] = useState<any>(null);
  const [serviceError, setServiceError] = useState<string | null>(null);
  const [serviceLoading, setServiceLoading] = useState<boolean>(false);

  // Example 2: Using the API client directly
  const [directResponse, setDirectResponse] = useState<any>(null);
  const [directError, setDirectError] = useState<string | null>(null);
  const [directLoading, setDirectLoading] = useState<boolean>(false);

  // Example 3: Using the useApiCall hook (recommended approach)
  const { 
    data: hookData, 
    loading: hookLoading, 
    error: hookError, 
    execute: executeTestCall 
  } = useApiCall(frontendApiService.testApiCall);

  // Example 1: Using the API service
  const handleServiceApiCall = async () => {
    try {
      setServiceLoading(true);
      setServiceError(null);
      const data = await frontendApiService.getSession();
      setServiceResponse(data);
    } catch (error) {
      console.error('API service error:', error);
      setServiceError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setServiceLoading(false);
    }
  };

  // Example 2: Using the API client directly
  const handleDirectApiCall = async () => {
    try {
      setDirectLoading(true);
      setDirectError(null);
      const response = await frontendApiClient.get('/session');
      setDirectResponse(response.data);
    } catch (error) {
      console.error('Direct API call error:', error);
      setDirectError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setDirectLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-4 border rounded-lg">
      <h2 className="text-xl font-bold">API Call Examples</h2>
      
      {/* Example 1: Using the API service */}
      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold mb-2">Example 1: Using API Service</h3>
        <button
          onClick={handleServiceApiCall}
          disabled={serviceLoading}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-green-300"
        >
          {serviceLoading ? "Loading..." : "Call API Service"}
        </button>
        
        {serviceError && (
          <div className="mt-2 p-2 bg-red-100 text-red-700 rounded">
            Error: {serviceError}
          </div>
        )}
        
        {serviceResponse && (
          <div className="mt-2 p-2 bg-gray-100 rounded">
            <p className="font-bold">Response:</p>
            <pre className="text-xs overflow-auto max-h-40">
              {JSON.stringify(serviceResponse, null, 2)}
            </pre>
          </div>
        )}
      </div>
      
      {/* Example 2: Using the API client directly */}
      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold mb-2">Example 2: Using API Client Directly</h3>
        <button
          onClick={handleDirectApiCall}
          disabled={directLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
        >
          {directLoading ? "Loading..." : "Call API Directly"}
        </button>
        
        {directError && (
          <div className="mt-2 p-2 bg-red-100 text-red-700 rounded">
            Error: {directError}
          </div>
        )}
        
        {directResponse && (
          <div className="mt-2 p-2 bg-gray-100 rounded">
            <p className="font-bold">Response:</p>
            <pre className="text-xs overflow-auto max-h-40">
              {JSON.stringify(directResponse, null, 2)}
            </pre>
          </div>
        )}
      </div>
      
      {/* Example 3: Using the useApiCall hook */}
      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold mb-2">Example 3: Using useApiCall Hook (Recommended)</h3>
        <button
          onClick={() => executeTestCall()}
          disabled={hookLoading}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:bg-purple-300"
        >
          {hookLoading ? "Loading..." : "Call API with Hook"}
        </button>
        
        {hookError && (
          <div className="mt-2 p-2 bg-red-100 text-red-700 rounded">
            Error: {hookError.message}
          </div>
        )}
        
        {hookData && (
          <div className="mt-2 p-2 bg-gray-100 rounded">
            <p className="font-bold">Response:</p>
            <pre className="text-xs overflow-auto max-h-40">
              {JSON.stringify(hookData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
} 
