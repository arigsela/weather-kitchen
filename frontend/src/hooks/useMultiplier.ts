import { useAppStore } from "../store/appStore";

export function useMultiplier(defaultFamilySize = 4): number {
  // In a real scenario this would read from the family data
  // For now, use a simple ceil(family_size / 2) formula
  const familySize = useAppStore((s) => s.currentFamilyId) ? defaultFamilySize : 4;
  return Math.ceil(familySize / 2);
}
