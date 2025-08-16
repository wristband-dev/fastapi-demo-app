import React, { useState } from 'react';
import { useWristbandAuth } from '@wristband/react-client-auth';

import { Logo, DarkLogo } from 'images';
import { AuthStatus, HelloWorldTester, LoginButton, LogoutButton, NicknameGenerator, TabButton } from 'components';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'cookie' | 'token'>('cookie');

  /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
  const { isAuthenticated } = useWristbandAuth();

  return (
    <div
      className={`font-geist-sans flex flex-col items-center justify-items-center min-h-screen p-8 pt-16 bg-slate-50 dark:bg-slate-900`}
    >
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-2xl">
        <div className="flex items-center flex-col">
          <img src={Logo} alt="Wristband Logo" width={180} height={38} className="block dark:hidden" />
          <img src={DarkLogo} alt="Wristband Logo" width={180} height={38} className="hidden dark:block" />
          <h1 className="mt-4 text-2xl mb-1">Welcome to the FastAPI Demo</h1>
        </div>
        <AuthStatus />
        {!isAuthenticated && <LoginButton />}
        {isAuthenticated && (
          <div className="flex flex-col gap-2 w-full">
            <hr className="my-2" />
            <h2 className="font-bold text-lg mt-2 mb-1">Mafia Nickname Generator</h2>
            <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
              <TabButton
                title="Test with Cookie"
                isActive={activeTab === 'cookie'}
                onClick={() => setActiveTab('cookie')}
              />
              <TabButton
                title="Test with Token"
                isActive={activeTab === 'token'}
                onClick={() => setActiveTab('token')}
              />
            </div>
            <div className="flex flex-col gap-2 w-full">
              {activeTab === 'cookie' && <NicknameGenerator />}
              {activeTab === 'token' && <HelloWorldTester />}
            </div>
            <hr className="mt-6" />
            <LogoutButton />
          </div>
        )}
      </main>
    </div>
  );
}
