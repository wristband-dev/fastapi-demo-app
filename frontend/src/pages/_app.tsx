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
      disableRedirectOnUnauthenticated={true}
    >
      <Component {...pageProps} />
    </WristbandAuthProvider>
  )
}