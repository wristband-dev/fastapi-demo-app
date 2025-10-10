import React, { useState } from 'react';
import { useWristbandAuth, useWristbandSession } from '@wristband/react-client-auth';

import { SessionData } from 'types';

export function AuthStatus() {
  const [isExpanded, setIsExpanded] = useState(false);

  /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
  const { isAuthenticated, isLoading } = useWristbandAuth();
  const { userId, tenantId, metadata } = useWristbandSession<SessionData>();

  const toggleAccordion = () => {
    setIsExpanded(!isExpanded);
  };

  if (isLoading) {
    return (
      <div className="p-4 bg-gray-100 dark:bg-gray-900 rounded w-full text-center">
        <p>Loading session...</p>
      </div>
    );
  }

  return (
    <>
      {isAuthenticated && metadata ? (
        <div className="p-4 bg-green-100 dark:bg-green-900 rounded w-full">
          <button
            onClick={toggleAccordion}
            className="w-full text-left flex items-center justify-between font-bold mb-2 hover:bg-green-200 dark:hover:bg-green-800 hover:text-green-800 dark:hover:text-green-200 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 rounded-lg p-2 border border-transparent hover:border-green-300 dark:hover:border-green-600 cursor-pointer hover:shadow-sm"
          >
            <span>Session active (Click to view)</span>
            <svg
              className={`w-4 h-4 transform transition-transform duration-200 ${
                isExpanded ? 'rotate-180' : 'rotate-0'
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {isExpanded && (
            <div className="bg-white dark:bg-gray-800 p-2 rounded max-h-40 overflow-auto animate-in slide-in-from-top-2 duration-200">
              <pre className="text-xs whitespace-pre-wrap break-all">
                {JSON.stringify({ userId, tenantId, ...metadata }, null, 2)}
              </pre>
            </div>
          )}
        </div>
      ) : (
        <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded w-full">
          <p>No active session and/or CSRF token</p>
        </div>
      )}
    </>
  );
}
