export type SessionData = {
  is_authenticated: boolean;
  access_token: string;
  expires_at: number;
  refresh_token?: string;
  user_id: string;
  tenant_id: string;
  idp_name: string;
  tenant_domain_name: string;
  tenant_custom_domain?: string;
  csrf_token: string;
};
