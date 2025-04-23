import React, { createContext, useEffect, useState } from 'react';

import { redirectToLogin, redirectToLogout, isUnauthorizedError } from '@/utils/helpers';
import { frontendApiService } from '@/services/frontend-api-service';


const AuthContext = createContext({
  isAuthenticated: false,
  isLoading: true,
  sessionData: null,
  login: () => {},
  logout: () => {},
  refreshSession: () => Promise.resolve(),
});

function AuthProvider({ children }: { children: React.ReactNode }) {
  // Auth Context State
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [sessionData, setSessionData] = useState<any>(null);

  const login = () => {
    if (typeof window !== 'undefined') {
      window.location.href = 'http://localhost:8080/api/auth/login';
    }
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      // Clear session data locally
      setSessionData(null);
      setIsAuthenticated(false);
      
      // Redirect to logout endpoint
      window.location.href = 'http://localhost:8080/api/auth/logout';
    }
  };

  const refreshSession = async () => {
    try {
      const sessionData = await frontendApiService.getSession();
      setSessionData(sessionData);
      setIsAuthenticated(true);
      setIsLoading(false);
      return sessionData;
    } catch (error: any) {
      setIsLoading(false);
      setIsAuthenticated(false);
      setSessionData(null);
      
      if (isUnauthorizedError(error)) {
        // If user is not authenticated, don't redirect automatically
        return null;
      }
    }
  };

  // Bootstrap the application with the authenticated user's session data.
  useEffect(() => {
    const fetchSession = async () => {
      /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
      const data = await refreshSession();
        
      if (!data) {
        setIsLoading(false);
      }
    };

    fetchSession();
  }, []);

  return (
    <AuthContext.Provider
      value={{ 
        isAuthenticated, 
        isLoading, 
        sessionData,
        login,
        logout,
        refreshSession
      }}
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
