export class ApiError extends Error {
  status?: number;
  statusText?: string;
  response?: Response;

  constructor(message: string) {
    super(message);
    this.name = 'ApiError';
  }
}