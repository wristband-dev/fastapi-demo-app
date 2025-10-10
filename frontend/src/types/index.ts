// Type that maps to the `metadata` returned from the FastAPI Session Endpoint.
export type SessionData = {
  isAuthenticated: boolean;
  accessToken: string;
  expiresAt: number;
  tenantName: string;
  identityProviderName: string;
  csrfToken: string;
  customField: string;
  refreshToken?: string;
  tenantCustomDomain?: string;
};
