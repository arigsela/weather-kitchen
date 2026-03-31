import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/client";
import { useCurrentUser } from "../../hooks/useCurrentUser";

export function useUserIngredients() {
  const { currentUserId } = useCurrentUser();

  return useQuery({
    queryKey: ["user-ingredients", currentUserId],
    queryFn: async () => {
      const res = await apiClient
        .get(`api/v1/users/${currentUserId}/ingredients`)
        .json<{ ingredients: string[] }>();
      return res.ingredients;
    },
    enabled: !!currentUserId,
    initialData: [],
  });
}
