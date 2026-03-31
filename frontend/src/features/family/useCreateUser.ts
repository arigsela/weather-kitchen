import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createUser } from "../../api/users";
import { useCurrentFamily } from "../../hooks/useCurrentFamily";

export function useCreateUser() {
  const queryClient = useQueryClient();
  const { currentFamilyId } = useCurrentFamily();

  return useMutation({
    mutationFn: (data: { name: string; emoji?: string }) => createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users", currentFamilyId] });
    },
  });
}
