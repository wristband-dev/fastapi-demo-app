const VANITY_DOMAIN_TO_USE =
  process.env.PUBLIC_DEMO === 'ENABLED' ? 'app.perkparty.club' : 'app.dev-perkparty.club:6001';

export const IS_LOCALHOST = process.env.DOMAIN_FORMAT === 'LOCALHOST';
export const PERKPARTY_HOST = IS_LOCALHOST ? 'localhost:6001' : VANITY_DOMAIN_TO_USE;
export const PERK_PARTY_PROTOCOL = process.env.PUBLIC_DEMO === 'ENABLED' ? 'https' : 'http';

export const APPLICATION_LOGIN_URL = `https://${process.env.APPLICATION_DOMAIN}/login`;
export const WRISTBAND_API_URL = `https://${process.env.APPLICATION_DOMAIN}/api/v1`;
export const JSON_MEDIA_TYPE = 'application/json;charset=UTF-8';
export const LOGIN_STATE_COOKIE_PREFIX = 'login:';
export const LOGIN_STATE_COOKIE_SECRET = '7ffdbecc-ab7d-4134-9307-2dfcc52f7475';
export const SESSION_COOKIE_NAME = 'session';
export const SESSION_COOKIE_SECRET = '96bf13d5-b5c1-463a-812c-0d8db87c0ec5';
export const HTTP_401_STATUS = { status: 401 };
export const UNAUTHORIZED = { statusText: 'Unauthorized' };
export const LOGIN_REQUIRED_ERROR: string = 'login_required';
export const FORM_URLENCOED_MEDIA_TYPE: string = 'application/x-www-form-urlencoded';
export const VIP_HOST_ROLE_NAME = 'vip-host';

// CSRF constants
export const CSRF_TOKEN_COOKIE_NAME = 'XSRF-TOKEN';
export const CSRF_TOKEN_HEADER_NAME = 'x-xsrf-token';
