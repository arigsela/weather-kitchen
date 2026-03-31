import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../api/client";
import { useCurrentUser } from "../../hooks/useCurrentUser";

export function useSaveIngredients() {
  const queryClient = useQueryClient();
  const { currentUserId } = useCurrentUser();

  return useMutation({
    mutationFn: async (ingredients: string[]) => {
      await apiClient.put(`api/v1/users/${currentUserId}/ingredients`, { json: { ingredients } });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-ingredients", currentUserId] });
    },
  });
}
