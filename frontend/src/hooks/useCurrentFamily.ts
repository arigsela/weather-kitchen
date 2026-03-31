import { useAppStore } from "../store/appStore";

export function useCurrentFamily() {
  const currentFamilyId = useAppStore((s) => s.currentFamilyId);
  const setCurrentFamily = useAppStore((s) => s.setCurrentFamily);
  return { currentFamilyId, setCurrentFamily };
}
