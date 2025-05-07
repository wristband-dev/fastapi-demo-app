import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { WristbandAuthProvider } from "@wristband/react-client-auth";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <WristbandAuthProvider
      loginUrl="http://localhost:8080/api/auth/login"
      logoutUrl="http://localhost:8080/api/auth/logout"
      sessionUrl="http://localhost:8080/api/auth/session"
      disableRedirectOnUnauthenticated={true}
    >
      <Component {...pageProps} />
    </WristbandAuthProvider>
  )
}