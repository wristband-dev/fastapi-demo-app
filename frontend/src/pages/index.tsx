import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { useState } from "react";
import { useWristbandAuth, redirectToLogin, redirectToLogout, useWristbandSession } from "@wristband/react-client-auth";
import TransactionPortal from "@/components/TransactionPortal";
import WristbandTestComponents from "@/components/WristbandTestComponents";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"], 
});

export default function Home() {
  const [logoutMessage, setLogoutMessage] = useState<string | null>(null);
  const { isAuthenticated, isLoading} = useWristbandAuth();
  const { metadata } = useWristbandSession();
  const [cookies, setCookies] = useState<string>("");

  const handleLogout = () => {
    setLogoutMessage("Logging out...");
    redirectToLogout('http://localhost:8080/api/auth/logout');
  };

  const handleLogin = () => {
    redirectToLogin('http://localhost:8080/api/auth/login');
  };

  return (
    <div
      className={`${geistSans.variable} ${geistMono.variable} grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]`}
    >
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-2xl">
        <div className="flex items-center">
          <Image
            src="/wristband_logo_dark.svg"
            alt="Wristband Logo"
            width={180}
            height={38}
            priority
          />
        </div>
        {logoutMessage && (
          <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded w-full text-center">
            <p>{logoutMessage}</p>
          </div>
        )}
        {isLoading ? (
          <p>Loading session...</p>
        ) : isAuthenticated && metadata ? (
          <div className="p-4 bg-green-100 dark:bg-green-900 rounded w-full">
            <p className="font-bold mb-2">Session active:</p>
            <div className="bg-white dark:bg-gray-800 p-2 rounded max-h-40 overflow-auto">
              <pre className="text-xs whitespace-pre-wrap break-all">{JSON.stringify(metadata, null, 2)}</pre>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded w-full">
            <p>No active session</p>
            <p className="mt-2 text-xs">Cookies: {document?.cookie || ""}</p>
          </div>
        )}

        {!isAuthenticated && (
          <div className="flex flex-col gap-2 w-full">
            <button
              onClick={handleLogin}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Login
            </button>
          </div>
        )}
        {isAuthenticated && (
          <div className="flex flex-col gap-2 w-full">
            <h2 className="font-bold text-lg mt-2 mb-1">Wristband API Tests</h2>
            <WristbandTestComponents />
            
            <h2 className="font-bold text-lg mt-6 mb-1">Transaction Management (Firestore)</h2>
            <TransactionPortal />
            
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 mt-4"
            >
              Logout
            </button>
          </div>
        )}
      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
      </footer>
    </div>
  );
}
