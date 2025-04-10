import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";

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
  const [sessionData, setSessionData] = useState<any>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [cookies, setCookies] = useState<string>("");
  const router = useRouter();

  useEffect(() => {
    // Display cookies for debugging
    setCookies(document.cookie);

    const fetchSessionData = async () => {
      try {
        console.log("Fetching session data...");
        const res = await fetch("http://localhost:8080/api/auth/session", {
          method: "GET",
          credentials: "include", // Include cookies in the request
          headers: {
            "Accept": "application/json",
          }
        });

        console.log("Session response status:", res.status);
        console.log("Session response headers:", Object.fromEntries([...res.headers.entries()]));

        if (!res.ok) {
          const errorText = await res.text();
          console.error(`Failed to fetch session data: ${res.status}`, errorText);
          setSessionLoading(false);
          return;
        }

        try {
          const data = await res.json();
          console.log("Session data received:", data);
          setSessionData(data);
        } catch (jsonError) {
          console.error("Error parsing session response as JSON:", jsonError);
          const text = await res.text();
          console.log("Raw response:", text);
          setResponse(`Error parsing session data: ${text}`);
        }
      } catch (error) {
        console.error("Error fetching session data:", error);
      } finally {
        setSessionLoading(false);
      }
    };

    fetchSessionData();
  }, []);

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
      console.log("Testing session endpoint...");
      const res = await fetch("http://localhost:8080/api/auth/session", {
        method: "GET",
        credentials: "include", // Include cookies in the request
      });

      console.log("Session test status:", res.status);
      console.log("Session test headers:", Object.fromEntries([...res.headers.entries()]));

      if (!res.ok) {
        const errorText = await res.text();
        console.error(`Session test failed: ${res.status}`, errorText);
        setResponse(`Session test failed: ${res.status} - ${errorText}`);
        return;
      }

      const data = await res.json();
      console.log("Session test data:", data);
      setResponse(`Session test response: ${JSON.stringify(data)}`);
      setSessionData(data);
    } catch (error) {
      console.error("Error testing session:", error);
      setResponse(`Error testing session: ${error}`);
    }
  };

  const handleLogout = () => {
    if (!!window) {
      console.log("Initiating logout process...");
      
      // Clear session data locally
      setSessionData(null);
      
      // Display logout message
      setLogoutMessage("Logging out...");
      
      // Log cookies before logout
      console.log("Cookies before logout:", document.cookie);
      
      // Redirect to logout endpoint
      console.log("Redirecting to logout endpoint");
      window.location.href = 'http://localhost:8080/api/auth/logout';
    }
  };

  const handleLogin = () => {
    if (!!window) {
      window.location.href = 'http://localhost:8080/api/auth/login';
    }
  };

  return (
    <div
      className={`${geistSans.variable} ${geistMono.variable} grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]`}
    >
      <main className="flex flex-col gap-8 row-start-2 items-center w-full max-w-2xl">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={180}
          height={38}
          priority
        />
        {logoutMessage && (
          <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded w-full text-center">
            <p>{logoutMessage}</p>
          </div>
        )}
        {sessionLoading ? (
          <p>Loading session...</p>
        ) : sessionData ? (
          <div className="p-4 bg-green-100 dark:bg-green-900 rounded w-full">
            <p className="font-bold mb-2">Session active:</p>
            <div className="bg-white dark:bg-gray-800 p-2 rounded max-h-40 overflow-auto">
              <pre className="text-xs whitespace-pre-wrap break-all">{JSON.stringify(sessionData, null, 2)}</pre>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded w-full">
            <p>No active session</p>
            <p className="mt-2 text-xs">Cookies: {cookies}</p>
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
        {!sessionData && (
          <div className="flex flex-col gap-2 w-full">
            <button
              onClick={handleLogin}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Login
            </button>
          </div>
        )}
        {sessionData && (
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
