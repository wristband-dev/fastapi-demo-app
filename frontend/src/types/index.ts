export type SessionData = {
  isAuthenticated: boolean;
  accessToken: string;
  expiresAt: number;
  refreshToken?: string;
  userId: string;
  tenantId: string;
  idpName: string;
  tenantDomainName: string;
  tenantCustomDomain?: string;
  csrfToken: string;
};
