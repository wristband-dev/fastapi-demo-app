import React, { createContext, useEffect, useState } from 'react';

import { redirectToLogin, redirectToLogout, isUnauthorizedError } from '@/utils/helpers';
import { frontendApiService } from '@/services/frontend-api-service';


const AuthContext = createContext({
  isAuthenticated: false,
  isLoading: true,
});

function AuthProvider({ children }: { children: React.ReactNode }) {
  // Auth Context State
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Bootstrap the application with the authenticated user's session data.
  useEffect(() => {
    const fetchSession = async () => {
      try {
        /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
        const sessionData = await frontendApiService.getSession();
        const { isAuthenticated } = sessionData;

        if (isAuthenticated) {
          setIsAuthenticated(true);
          setIsLoading(false);
        } else {
          redirectToLogout();
        }
        
      } catch (error: any) {
        console.log(error);

        if (isUnauthorizedError(error)) {
          // We want to preserve the page route that the user lands on when they come back after re-authentication.
          redirectToLogin();
        } else {
          redirectToLogout();
        }
      }
    };

    fetchSession();
  }, []);

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, isLoading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

function useWristband() {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useWristband must be used within an AuthProvider');
  }
  return context;
}

export { AuthProvider, useWristband };
