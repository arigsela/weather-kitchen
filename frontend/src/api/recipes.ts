import { publicClient } from "./client";
import type { Recipe, WeatherStats, WeatherType, CategoryType } from "../types/recipe";

interface FetchRecipesParams {
  weather?: WeatherType;
  category?: CategoryType;
  tags?: string[];
  page?: number;
  limit?: number;
}

interface RecipeListResponse {
  total: number;
  limit: number;
  offset: number;
  items: Recipe[];
}

export interface RecipeListResult {
  items: Recipe[];
  total: number;
  page: number;
  pages: number;
}

export async function fetchRecipes(params: FetchRecipesParams = {}): Promise<RecipeListResult> {
  const searchParams: Record<string, string> = {};
  if (params.weather) searchParams.weather = params.weather;
  if (params.category) searchParams.category = params.category;
  if (params.tags?.length) searchParams.tags = params.tags.join(",");
  const limit = params.limit ?? 12;
  const page = params.page ?? 1;
  searchParams.limit = String(limit);
  searchParams.offset = String((page - 1) * limit);

  const res = await publicClient.get("api/v1/recipes", { searchParams }).json<RecipeListResponse>();

  return {
    items: res.items,
    total: res.total,
    page,
    pages: Math.ceil(res.total / limit) || 1,
  };
}

export async function fetchRecipeById(id: string): Promise<Recipe> {
  return publicClient.get(`api/v1/recipes/${id}`).json<Recipe>();
}

export async function fetchWeatherStats(): Promise<WeatherStats[]> {
  const res = await publicClient
    .get("api/v1/stats/recipes-per-weather")
    .json<{ stats: WeatherStats[] }>();
  return res.stats;
}
