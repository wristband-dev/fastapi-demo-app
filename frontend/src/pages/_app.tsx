import type { AppProps } from "next/app";
import { WristbandAuthProvider } from "@wristband/react-client-auth";

import "@/styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  return (
    /* WRISTBAND_TOUCHPOINT - AUTHENTICATION */
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
