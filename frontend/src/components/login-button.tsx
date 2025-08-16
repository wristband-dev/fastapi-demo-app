import React from 'react';
import { redirectToLogin } from '@wristband/react-client-auth';

export function LoginButton() {
  const handleLogin = () => {
    redirectToLogin('/api/auth/login');
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      <button onClick={handleLogin} className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
        Login
      </button>
    </div>
  );
}
