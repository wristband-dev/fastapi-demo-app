import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Routes, Route } from 'react-router';
import { WristbandAuthProvider } from '@wristband/react-client-auth';

import './index.css';

import { HomePage } from 'pages';

// Component that only renders router for non-API routes
function App() {
  // Don't render React Router for API routes
  if (window.location.pathname.startsWith('/api')) {
    return null;
  }

  return (
    <Routes>
      <Route path="/home" element={<HomePage />} />
      <Route path="*" element={<Navigate replace to="/home" />} />
    </Routes>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      {/* WRISTBAND_TOUCHPOINT - AUTHENTICATION */}
      <WristbandAuthProvider
        loginUrl={'api/auth/login'}
        sessionUrl={'api/auth/session'}
        tokenUrl={'api/auth/token'}
        disableRedirectOnUnauthenticated={true} // Prevents automatic redirects when not authenticated
      >
        <App />
      </WristbandAuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
