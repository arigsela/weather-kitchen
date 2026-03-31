import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../api/client";
import { useCurrentUser } from "../../hooks/useCurrentUser";
import type { FavoriteItem } from "./useFavorites";

export function useToggleFavorite() {
  const queryClient = useQueryClient();
  const { currentUserId } = useCurrentUser();

  return useMutation({
    mutationFn: async ({ recipeId, isFavorite }: { recipeId: string; isFavorite: boolean }) => {
      if (isFavorite) {
        await apiClient.delete(`api/v1/users/${currentUserId}/favorites/${recipeId}`);
      } else {
        await apiClient.put(`api/v1/users/${currentUserId}/favorites/${recipeId}`);
      }
    },
    onMutate: async ({ recipeId, isFavorite }) => {
      await queryClient.cancelQueries({ queryKey: ["favorites", currentUserId] });
      const previous = queryClient.getQueryData<FavoriteItem[]>(["favorites", currentUserId]);

      if (isFavorite) {
        queryClient.setQueryData<FavoriteItem[]>(["favorites", currentUserId], (old = []) =>
          old.filter((r) => r.recipe_id !== recipeId),
        );
      }

      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["favorites", currentUserId], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["favorites", currentUserId] });
    },
  });
}
