import axios from 'axios';
import config from '@/lib/config';

// Axios has XSRF token handling by default.  We still specify the values in the config
// here merely to be explicit about which names are being used under the hood.
const JSON_MEDIA_TYPE = 'application/json;charset=UTF-8';

// Extract key values from config
const appHost = config.app.host;
const backendPort = config.backend.port;

const defaultOptions = {
  // Set up baseURL based on the app host and backend port from config
  baseURL: `${appHost}:${backendPort}/api`,
  headers: { 'Content-Type': JSON_MEDIA_TYPE, Accept: JSON_MEDIA_TYPE }
};

const frontendApiClient = axios.create(defaultOptions);

export default frontendApiClient;