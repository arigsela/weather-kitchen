import ky, { type KyInstance } from "ky";
import { useAppStore } from "../store/appStore";

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

async function refreshAccessToken(): Promise<boolean> {
  const { refreshToken, setTokens, clearTokens } = useAppStore.getState();
  if (!refreshToken) return false;

  try {
    const res = await ky
      .post(`${API_URL}/api/v1/auth/refresh`, {
        json: { refresh_token: refreshToken },
      })
      .json<{
        access_token: string;
        refresh_token: string;
        token_type: string;
        expires_in: number;
      }>();

    setTokens(res.access_token, res.refresh_token, res.expires_in);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

export const apiClient: KyInstance = ky.create({
  prefixUrl: API_URL,
  hooks: {
    beforeRequest: [
      (request) => {
        const { accessToken } = useAppStore.getState();
        if (accessToken) {
          request.headers.set("Authorization", `Bearer ${accessToken}`);
        }
      },
    ],
    afterResponse: [
      async (request, _options, response) => {
        if (response.status === 401 && !request.headers.get("X-Retry")) {
          const refreshed = await refreshAccessToken();
          if (refreshed) {
            const { accessToken } = useAppStore.getState();
            request.headers.set("Authorization", `Bearer ${accessToken}`);
            request.headers.set("X-Retry", "true");
            return ky(request);
          }
        }
        return response;
      },
    ],
  },
});

export const publicClient: KyInstance = ky.create({
  prefixUrl: API_URL,
});
