import { useQuery } from "@tanstack/react-query";
import { fetchRecipes } from "../../api/recipes";
import type { WeatherType, CategoryType } from "../../types/recipe";

interface UseRecipesParams {
  weather?: WeatherType;
  category?: CategoryType;
  tags?: string[];
  page?: number;
  limit?: number;
}

export function useRecipes(params: UseRecipesParams = {}) {
  return useQuery({
    queryKey: ["recipes", params],
    queryFn: () => fetchRecipes(params),
  });
}
