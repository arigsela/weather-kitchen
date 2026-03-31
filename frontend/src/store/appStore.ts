import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  currentFamilyId: string | null;
  currentUserId: string | null;
  hasCompletedSetup: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  tokenExpiry: number | null;

  setTokens: (accessToken: string, refreshToken: string, expiresIn: number) => void;
  clearTokens: () => void;
  setCurrentFamily: (familyId: string) => void;
  setCurrentUser: (userId: string) => void;
  setSetupComplete: () => void;
  reset: () => void;
}

const initialState = {
  currentFamilyId: null,
  currentUserId: null,
  hasCompletedSetup: false,
  accessToken: null,
  refreshToken: null,
  tokenExpiry: null,
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      ...initialState,

      setTokens: (accessToken, refreshToken, expiresIn) =>
        set({
          accessToken,
          refreshToken,
          tokenExpiry: Date.now() + expiresIn * 1000,
        }),

      clearTokens: () =>
        set({
          accessToken: null,
          refreshToken: null,
          tokenExpiry: null,
          currentFamilyId: null,
          currentUserId: null,
          hasCompletedSetup: false,
        }),

      setCurrentFamily: (familyId) => set({ currentFamilyId: familyId }),
      setCurrentUser: (userId) => set({ currentUserId: userId }),
      setSetupComplete: () => set({ hasCompletedSetup: true }),
      reset: () => set(initialState),
    }),
    {
      name: "weather-kitchen-store",
      partialize: (state) => ({
        currentFamilyId: state.currentFamilyId,
        currentUserId: state.currentUserId,
        hasCompletedSetup: state.hasCompletedSetup,
        refreshToken: state.refreshToken,
      }),
    },
  ),
);
