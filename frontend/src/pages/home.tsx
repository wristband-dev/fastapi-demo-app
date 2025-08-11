import React, { useState, useEffect } from 'react';
import { isAxiosError } from 'axios';
import { useWristbandAuth, redirectToLogin, redirectToLogout, useWristbandSession } from '@wristband/react-client-auth';

import frontendApiClient from 'client/frontend-api-client';
import { Logo, DarkLogo } from 'images';
import { SessionData } from 'types';

export default function HomePage() {
  const [isLoggingOut, setIsLoggingOut] = useState<boolean>(false);
  const [isNicknameLoading, setIsNicknameLoading] = useState<boolean>(false);
  const [nickname, setNickname] = useState<string>('');

  /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
  const { isAuthenticated, isLoading } = useWristbandAuth();
  const { metadata } = useWristbandSession<SessionData>();
  const { tenant_domain_name: tenantDomainName } = metadata;

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
      redirectToLogin('/api/auth/login', { tenantDomain: tenantDomainName });
      window.alert('Authentication required.');
    } else {
      window.alert(`Error: ${error}`);
    }
  };

  const handleLogout = () => {
    setIsLoggingOut(true);
    redirectToLogout('/api/auth/logout');
  };

  const handleLogin = () => {
    redirectToLogin('/api/auth/login');
  };

  return (
    <div
      className={`font-geist-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 bg-slate-50 dark:bg-slate-900`}
    >
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-2xl">
        {/* Header */}
        <div className="flex items-center">
          <img src={Logo} alt="Wristband Logo" width={180} height={38} className="block dark:hidden" />
          <img src={DarkLogo} alt="Wristband Logo" width={180} height={38} className="hidden dark:block" />
        </div>

        {isLoggingOut && (
          <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded w-full text-center">
            <p>Logging out...</p>
          </div>
        )}

        {/* Authentication Status */}
        {isLoading ? (
          <div className="p-4 bg-gray-100 dark:bg-gray-900 rounded w-full text-center">
            <p>Loading session...</p>
          </div>
        ) : isAuthenticated && metadata ? (
          <div className="p-4 bg-green-100 dark:bg-green-900 rounded w-full">
            <p className="font-bold mb-2">Session active:</p>
            <div className="bg-white dark:bg-gray-800 p-2 rounded max-h-40 overflow-auto">
              <pre className="text-xs whitespace-pre-wrap break-all">{JSON.stringify(metadata, null, 2)}</pre>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded w-full">
            <p>No active session and/or CSRF token</p>
          </div>
        )}

        {/* Login Button */}
        {!isAuthenticated && (
          <div className="flex flex-col gap-2 w-full">
            <button onClick={handleLogin} className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
              Login
            </button>
          </div>
        )}

        {/* Authenticated User Options */}
        {isAuthenticated && (
          <div className="flex flex-col gap-2 w-full">
            <hr className="my-2" />

            {/* Nickname Generator */}
            <h2 className="font-bold text-lg mt-2 mb-1">Mafia Nickname Generator</h2>
            <div className="flex flex-col gap-2 w-full">
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
            </div>

            {/* Logout Button */}
            <button onClick={handleLogout} className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 mt-12">
              Logout
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
