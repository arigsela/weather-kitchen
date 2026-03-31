import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/client";
import { useCurrentUser } from "../../hooks/useCurrentUser";

export interface FavoriteItem {
  id: string;
  user_id: string;
  recipe_id: string;
  recipe_name: string;
  recipe_weather: string;
  added_at: string;
}

export function useFavorites() {
  const { currentUserId } = useCurrentUser();

  return useQuery({
    queryKey: ["favorites", currentUserId],
    queryFn: async () => {
      const res = await apiClient
        .get(`api/v1/users/${currentUserId}/favorites`)
        .json<{ favorites: FavoriteItem[]; total: number }>();
      return res.favorites;
    },
    enabled: !!currentUserId,
    initialData: [],
  });
}
