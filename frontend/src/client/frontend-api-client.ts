import axios from 'axios';

// Axios has XSRF token handling by default.  We still specify the values in the config
// here merely to be explicit about which names are being used under the hood.
const JSON_MEDIA_TYPE = 'application/json;charset=UTF-8';

const defaultOptions = {
  // Set up baseURL based on whether this is server-side or client-side
  // baseURL: typeof window !== 'undefined' ? `${window.location.origin}/api/v1` : undefined,
  baseURL: 'http://localhost:8080/api',
  headers: { 'Content-Type': JSON_MEDIA_TYPE, Accept: JSON_MEDIA_TYPE }
};

const frontendApiClient = axios.create(defaultOptions);

export default frontendApiClient;