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
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
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
          <div className="p-4 bg-green-100 dark:bg-green-900 rounded">
            <p>Session active: {JSON.stringify(sessionData)}</p>
          </div>
        ) : (
          <div className="p-4 bg-yellow-100 dark:bg-yellow-900 rounded">
            <p>No active session</p>
            <p className="mt-2 text-xs">Cookies: {cookies}</p>
          </div>
        )}
        <ol className="list-inside list-decimal text-sm text-center sm:text-left font-[family-name:var(--font-geist-mono)]">
          <li className="mb-2">
            Get started by editing{" "}
            <code className="bg-black/[.05] dark:bg-white/[.06] px-1 py-0.5 rounded font-semibold">
              src/pages/index.tsx
            </code>
            .
          </li>
          <li>Save and see your changes instantly.</li>
        </ol>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <a
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5"
            href="https://vercel.com/new?utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/vercel.svg"
              alt="Vercel logomark"
              width={20}
              height={20}
            />
            Deploy now
          </a>
          <a
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:min-w-44"
            href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Read our docs
          </a>
        </div>
        <div className="flex flex-col gap-2">
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
          {response && <p className="mt-2 text-sm">{response}</p>}
        </div>
        {!sessionData && (
          <div className="flex flex-col gap-2">
            <button
              onClick={handleLogin}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Login
            </button>
          </div>
        )}
        {sessionData && (
          <div className="flex flex-col gap-2">
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
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=default-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
