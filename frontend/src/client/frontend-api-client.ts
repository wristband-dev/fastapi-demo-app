import axios from 'axios';
import getConfig from 'next/config';

const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} };

// Axios has XSRF token handling by default.  We still specify the values in the config
// here merely to be explicit about which names are being used under the hood.
const JSON_MEDIA_TYPE = 'application/json;charset=UTF-8';

// Extract key values from publicRuntimeConfig
// Provide defaults if values might be undefined at build time but available at runtime
const appHost = publicRuntimeConfig.appHost || 'http://localhost:3001'; // Default, if not set
const backendPort = publicRuntimeConfig.backendPort || 8000; // Default, if not set

const defaultOptions = {
  // Set up baseURL based on the app host and backend port from publicRuntimeConfig
  baseURL: `${appHost}:${backendPort}/api`,
  headers: { 'Content-Type': JSON_MEDIA_TYPE, Accept: JSON_MEDIA_TYPE }
};

const frontendApiClient = axios.create(defaultOptions);

export default frontendApiClient;