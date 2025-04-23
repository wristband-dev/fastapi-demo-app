import { AxiosError } from 'axios';

export function redirectToLogout() {
    window.location.href = `http://localhost:8080/api/auth/logout`;
}
  
export function redirectToLogin() {
    const query = new URLSearchParams({ return_url: encodeURI(window.location.href) }).toString();
    window.location.href = `http://localhost:8080/api/auth/login?${query}`;
}

export function isUnauthorizedError(error: unknown) {
  if (!error) {
    return false;
  }

  if (!(error instanceof AxiosError)) {
    return false
  }

  console.log(error.response?.status);
  return error.response?.status === 401;
}