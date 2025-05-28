/**
 * Next.js App Component
 * 
 * This is the main application wrapper that sets up the Wristband authentication provider
 * and provides the authentication context to all pages.
 */
import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { WristbandAuthProvider } from "@wristband/react-client-auth";
import { loginUrl, logoutUrl, sessionUrl } from "@/lib/authConfig";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <WristbandAuthProvider
      loginUrl={loginUrl}
      logoutUrl={logoutUrl}
      sessionUrl={sessionUrl}
      disableRedirectOnUnauthenticated={true} // Prevents automatic redirects when not authenticated
    >
      <Component {...pageProps} />
    </WristbandAuthProvider>
  )
}