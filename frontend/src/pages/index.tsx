/**
 * Home Page
 * 
 * This is the main page of the application. It handles authentication status
 * and provides UI for login, logout and testing Wristband functionality.
 */
import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { useState, useEffect } from "react";
import { useWristbandAuth, redirectToLogin, redirectToLogout, useWristbandSession } from "@wristband/react-client-auth";
import WristbandTestComponents from "@/components/WristbandTestComponents";
import { loginUrl, logoutUrl } from "@/lib/authConfig";

// Load fonts
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
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated, isLoading } = useWristbandAuth();
  const { metadata } = useWristbandSession();

  /**
   * Handles user logout by redirecting to the logout URL
   */
  const handleLogout = () => {
    try {
      setLogoutMessage("Logging out...");
      redirectToLogout(logoutUrl);
    } catch (err) {
      setError("Failed to log out. Please try again.");
      console.error("Logout error:", err);
    }
  };

  /**
   * Handles user login by redirecting to the login URL
   */
  const handleLogin = () => {
    try {
      redirectToLogin(loginUrl);
    } catch (err) {
      setError("Failed to redirect to login. Please try again.");
      console.error("Login error:", err);
    }
  };

  // Clear error message after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <div
      className={`${geistSans.variable} ${geistMono.variable} grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]`}
    >
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-2xl">
        {/* Header */}
        <div className="flex items-center">
          <Image
            src="/wristband_logo_dark.svg"
            alt="Wristband Logo"
            width={180}
            height={38}
            priority
          />
        </div>

        {/* Error/Info Messages */}
        {error && (
          <div className="p-4 bg-red-100 dark:bg-red-900 rounded w-full text-center">
            <p>{error}</p>
          </div>
        )}
        
        {logoutMessage && (
          <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded w-full text-center">
            <p>{logoutMessage}</p>
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
            <p>No active session</p>
            <p className="mt-2 text-xs">Cookies: {document?.cookie || ""}</p>
          </div>
        )}

        {/* Login Button */}
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

        {/* Authenticated User Options */}
        {isAuthenticated && (
          <div className="flex flex-col gap-2 w-full">
            <h2 className="font-bold text-lg mt-2 mb-1">Wristband API Tests</h2>
            <WristbandTestComponents />
            
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
        {/* Footer content if needed */}
      </footer>
    </div>
  );
}
