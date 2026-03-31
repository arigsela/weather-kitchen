import { useAppStore } from "../store/appStore";

export function useCurrentUser() {
  const currentUserId = useAppStore((s) => s.currentUserId);
  const setCurrentUser = useAppStore((s) => s.setCurrentUser);
  return { currentUserId, setCurrentUser };
}
