/**
 * Next.js App Component
 * 
 * This is the main application wrapper that sets up the Wristband authentication provider
 * and provides the authentication context to all pages.
 */
import type { AppProps } from "next/app";
import { WristbandAuthProvider } from "@wristband/react-client-auth";

import "@/styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <WristbandAuthProvider
      loginUrl={'api/auth/login'}
      logoutUrl={'api/auth/logout'}
      sessionUrl={'api/session'}
      disableRedirectOnUnauthenticated={true} // Prevents automatic redirects when not authenticated
    >
      <Component {...pageProps} />
    </WristbandAuthProvider>
  )
}
