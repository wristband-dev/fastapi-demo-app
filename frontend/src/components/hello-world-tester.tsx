import React, { useState } from 'react';
import { useWristbandToken, redirectToLogin, useWristbandSession } from '@wristband/react-client-auth';

import { SessionData } from 'types';

export function HelloWorldTester() {
  const [isHelloWorldLoading, setIsHelloWorldLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

  /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
  const { getToken } = useWristbandToken();
  const { metadata } = useWristbandSession<SessionData>();
  const { tenant_domain_name: tenantDomainName } = metadata;

  const sayHello = async () => {
    try {
      setIsHelloWorldLoading(true);
      const token = await getToken();
      const response = await fetch('/api/hello', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: 'Hello' }),
      });

      if (!response.ok) {
        if ([401, 403].includes(response.status)) {
          redirectToLogin('/api/auth/login', { tenantDomain: tenantDomainName });
          window.alert('Authentication required.');
        } else {
          window.alert(`HTTP error! status: ${response.status}`);
        }
        return;
      }

      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      console.log(error);
      window.alert(`Unexpected error: ${error}`);
    } finally {
      setIsHelloWorldLoading(false);
    }
  };

  return (
    <>
      <h2 className="font-bold text-lg mb-1">Hello World Test</h2>
      <p>
        This button demonstrates token-based authentication as an alternative to cookies. The useWristbandToken() hook
        from the React SDK fetches and caches access tokens via the getToken() function. When clicked, this button sends
        the token manually in the Authorization header to the protected endpoint. The server&apos;s JwtAuthMiddleware
        validates the JWT token rather than relying on session cookies.
      </p>
      <button
        onClick={sayHello}
        disabled={isHelloWorldLoading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
      >
        {isHelloWorldLoading ? 'Saying Hello...' : 'Say Hello'}
      </button>

      {message && (
        <div className="mt-4 rounded border border-gray-300 dark:border-gray-700">
          <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
            <p className="font-bold text-sm">Response</p>
          </div>
          <div className="p-2 max-h-60 overflow-auto">
            <pre className="text-xs whitespace-pre-wrap break-all">{message}</pre>
          </div>
        </div>
      )}
    </>
  );
}
