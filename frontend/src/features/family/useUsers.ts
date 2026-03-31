import { useQuery } from "@tanstack/react-query";
import { listUsers } from "../../api/users";
import { useCurrentFamily } from "../../hooks/useCurrentFamily";

export function useUsers() {
  const { currentFamilyId } = useCurrentFamily();

  return useQuery({
    queryKey: ["users", currentFamilyId],
    queryFn: () => listUsers(),
    enabled: !!currentFamilyId,
  });
}
