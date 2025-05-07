import frontendApiClient from "@/client/frontend-api-client";


async function getSession() {
    const response = await frontendApiClient.get(`/auth/session`, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        Pragma: 'no-cache',
        Expires: '0',
      },
      withCredentials: true, // Include cookies in the request
    });

    return response.data;
  }

export const frontendApiService = {
    getSession,
};
