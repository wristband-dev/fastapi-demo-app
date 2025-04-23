import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { useState } from "react";
import { useWristband } from "@/context/auth-context";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"], 
});

export default function Home() {
  const [response, setResponse] = useState<string | null>(null);
  const [logoutMessage, setLogoutMessage] = useState<string | null>(null);
  const { isAuthenticated, isLoading, sessionData, login, logout, refreshSession } = useWristband();
  const [cookies, setCookies] = useState<string>("");

  const handleTestDecryptCookie = async () => {
    try {
      const res = await fetch("http://localhost:8080/api/auth/test_decrypt_cookie", {
        method: "GET",
        credentials: "include", // Include cookies in the request
      });

      if (!res.ok) {
        throw new Error("Failed to fetch");
      }

      const data = await res.text();
      setResponse(data);
    } catch (error) {
      console.error("Error:", error);
      setResponse("Error fetching data");
    }
  };

  const handleTestSession = async () => {
    try {
      console.log("Testing session refresh...");
      const data = await refreshSession();
      setResponse(`Session test response: ${JSON.stringify(data)}`);
    } catch (error) {
      console.error("Error testing session:", error);
      setResponse(`Error testing session: ${error}`);
    }
  };

  const handleLogout = () => {
    setLogoutMessage("Logging out...");
    logout();
  };

  const handleLogin = () => {
    login();
  };

  return (
    <div
      className={`${geistSans.variable} ${geistMono.variable} grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]`}
    >
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-2xl">
        <div className="flex items-center">
          <Image
            src="/wristband_logo.svg"
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
        ) : isAuthenticated && sessionData ? (
          <div className="p-4 bg-green-100 dark:bg-green-900 rounded w-full">
            <p className="font-bold mb-2">Session active:</p>
            <div className="bg-white dark:bg-gray-800 p-2 rounded max-h-40 overflow-auto">
              <pre className="text-xs whitespace-pre-wrap break-all">{JSON.stringify(sessionData, null, 2)}</pre>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded w-full">
            <p>No active session</p>
            <p className="mt-2 text-xs">Cookies: {document?.cookie || ""}</p>
          </div>
        )}

        <div className="flex flex-col gap-2 w-full">
          <button
            onClick={handleTestDecryptCookie}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Test Decrypt Cookie
          </button>
          <button
            onClick={handleTestSession}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 mt-2"
          >
            Test Session
          </button>
          {response && (
            <div className="mt-4 rounded border border-gray-300 dark:border-gray-700">
              <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
                <p className="font-bold text-sm">Response:</p>
              </div>
              <div className="p-2 max-h-60 overflow-auto">
                <pre className="text-xs whitespace-pre-wrap break-all">{
                  (() => {
                    try {
                      if (typeof response === 'string') {
                        // Try to parse as JSON first
                        const parsed = JSON.parse(response);
                        return JSON.stringify(parsed, null, 2);
                      }
                      return JSON.stringify(response, null, 2);
                    } catch (e) {
                      // If not valid JSON, just show as string
                      return response;
                    }
                  })()
                }</pre>
              </div>
            </div>
          )}
        </div>
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
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
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
