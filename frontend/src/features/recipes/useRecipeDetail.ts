import { useQuery } from "@tanstack/react-query";
import { fetchRecipeById } from "../../api/recipes";

export function useRecipeDetail(id: string | undefined) {
  return useQuery({
    queryKey: ["recipe", id],
    queryFn: () => fetchRecipeById(id!),
    enabled: !!id,
  });
}
