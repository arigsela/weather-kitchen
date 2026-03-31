import { useQuery } from "@tanstack/react-query";
import { getFamily } from "../../api/families";
import { useCurrentFamily } from "../../hooks/useCurrentFamily";

export function useFamily() {
  const { currentFamilyId } = useCurrentFamily();

  return useQuery({
    queryKey: ["family", currentFamilyId],
    queryFn: () => getFamily(currentFamilyId!),
    enabled: !!currentFamilyId,
  });
}
