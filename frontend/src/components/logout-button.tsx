import React, { useState } from 'react';
import { redirectToLogout } from '@wristband/react-client-auth';

export function LogoutButton() {
  const [isLoggingOut, setIsLoggingOut] = useState<boolean>(false);

  const handleLogout = () => {
    setIsLoggingOut(true);
    redirectToLogout('/api/auth/logout');
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      <button onClick={handleLogout} className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 mt-8">
        {isLoggingOut ? 'Logging out...' : 'Logout'}
      </button>
    </div>
  );
}
