import { AxiosError } from 'axios';

export function redirectToLogout() {
    // window.location.href = `${window.location.origin}/api/auth/logout`;
    window.location.href = `https://localhost:8080/api/auth/logout`;
}
  
export function redirectToLogin() {
    const query = new URLSearchParams({ return_url: encodeURI(window.location.href) }).toString();
    // window.location.href = `${window.location.origin}/api/auth/login?${query}`;
    window.location.href = `https://localhost:8080/api/auth/login?${query}`;
}

export function isUnauthorizedError(error: unknown) {
    if (!error) {
      return false;
    }
  
    if (error instanceof AxiosError) {
      return (error as AxiosError).response?.status === 401;
    }
  
    return false;
  }