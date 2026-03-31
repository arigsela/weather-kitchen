import { useCallback, useEffect, useRef, useState } from "react";
import { useAppStore } from "../store/appStore";
import { refreshTokens, logout as apiLogout } from "../api/auth";

export function useAuth() {
  const { accessToken, refreshToken, tokenExpiry, hasCompletedSetup, setTokens, clearTokens } =
    useAppStore();

  const [isBootstrapping, setIsBootstrapping] = useState(
    () => !accessToken && !!refreshToken,
  );

  // Guard against React StrictMode double-invoking this effect: the refresh
  // token is single-use (rotation). If the effect fires twice with the same
  // token, the second call will get 401 → clearTokens() → unexpected logout.
  const bootstrapCalledRef = useRef(false);

  // On mount: if we have a refreshToken but no accessToken, get a new one
  useEffect(() => {
    if (!accessToken && refreshToken && !bootstrapCalledRef.current) {
      bootstrapCalledRef.current = true;
      setIsBootstrapping(true);
      refreshTokens(refreshToken)
        .then((res) => setTokens(res.access_token, res.refresh_token, res.expires_in))
        .catch(() => clearTokens())
        .finally(() => setIsBootstrapping(false));
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-refresh token 1 minute before expiry
  useEffect(() => {
    if (!refreshToken || !tokenExpiry) return;

    const refreshAt = tokenExpiry - 60_000;
    const delay = refreshAt - Date.now();

    if (delay <= 0) {
      refreshTokens(refreshToken)
        .then((res) => setTokens(res.access_token, res.refresh_token, res.expires_in))
        .catch(() => clearTokens());
      return;
    }

    const timer = setTimeout(() => {
      refreshTokens(refreshToken)
        .then((res) => setTokens(res.access_token, res.refresh_token, res.expires_in))
        .catch(() => clearTokens());
    }, delay);

    return () => clearTimeout(timer);
  }, [refreshToken, tokenExpiry, setTokens, clearTokens]);

  const isAuthenticated = !!accessToken && !!refreshToken;

  const logout = useCallback(async () => {
    if (refreshToken) {
      try {
        await apiLogout(refreshToken);
      } catch {
        // Best-effort logout
      }
    }
    clearTokens();
  }, [refreshToken, clearTokens]);

  return { isAuthenticated, isBootstrapping, accessToken, hasCompletedSetup, logout };
}
