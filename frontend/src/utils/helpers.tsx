import { AxiosError } from 'axios';

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