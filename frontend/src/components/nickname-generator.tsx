import React, { useState, useEffect } from 'react';
import { isAxiosError } from 'axios';
import { useWristbandAuth, redirectToLogin, useWristbandSession } from '@wristband/react-client-auth';

import frontendApiClient from 'client/frontend-api-client';
import { SessionData } from 'types';

export function NicknameGenerator() {
  const [isNicknameLoading, setIsNicknameLoading] = useState<boolean>(false);
  const [nickname, setNickname] = useState<string>('');

  /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
  const { isAuthenticated, isLoading } = useWristbandAuth();
  const { metadata } = useWristbandSession<SessionData>();
  const { tenantName } = metadata;

  useEffect(() => {
    if (isAuthenticated && !isLoading && !nickname) {
      getNickname();
    }
  }, [isAuthenticated, isLoading]);

  const getNickname = async () => {
    try {
      setIsNicknameLoading(true);
      const response = await frontendApiClient.get('/nickname');
      setNickname(response.data.nickname);
    } catch (error) {
      handleApiError(error);
    } finally {
      setIsNicknameLoading(false);
    }
  };

  const generateNewNickname = async () => {
    try {
      setIsNicknameLoading(true);
      const response = await frontendApiClient.post('/nickname', null);
      setNickname(response.data.nickname);
    } catch (error) {
      handleApiError(error);
    } finally {
      setIsNicknameLoading(false);
    }
  };

  const handleApiError = (error: unknown) => {
    console.error(error);
    setNickname('');

    if (isAxiosError(error) && error.response && [401, 403].includes(error.response.status)) {
      redirectToLogin('/api/auth/login', { tenantName });
      window.alert('Authentication required.');
    } else {
      window.alert(`Error: ${error}`);
    }
  };

  return (
    <>
      <h2 className="font-bold text-lg mb-1">Mafia Nickname Generator</h2>
      <p>
        This button demonstrates cookie-based authentication for API calls. When clicked, the browser automatically
        sends the session cookie to the FastAPI server. The configured Axios client includes the CSRF token in the
        request headers for additional security. The server&apos;s &quot;require_session_auth&quot; Dependency validates
        the session cookie before allowing access to protected resources.
      </p>
      <button
        onClick={generateNewNickname}
        disabled={isNicknameLoading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
      >
        {isNicknameLoading ? 'Generating...' : 'Generate New Nickname'}
      </button>

      {nickname && (
        <div className="mt-4 rounded border border-gray-300 dark:border-gray-700">
          <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
            <p className="font-bold text-sm">Your Mafia Nickname:</p>
          </div>
          <div className="p-2 max-h-60 overflow-auto">
            <pre className="text-xs whitespace-pre-wrap break-all">{nickname}</pre>
          </div>
        </div>
      )}
    </>
  );
}
