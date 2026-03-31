export interface Recipe {
  id: string;
  name: string;
  emoji: string;
  why: string;
  tip: string;
  serves: number;
  weather: WeatherType;
  category: CategoryType;
  version_added: string;
  ingredients: RecipeIngredient[];
  steps: RecipeStep[];
  tags: { id: string; tag: string }[];
  created_at: string;
  updated_at: string;
}

export interface RecipeIngredient {
  id: string;
  ingredient_text: string;
  sort_order: number;
}

export interface RecipeStep {
  id: string;
  step_number: number;
  step_text: string;
}

export type WeatherType =
  | "sunny"
  | "rainy"
  | "snowy"
  | "hot"
  | "windy"
  | "cloudy"
  | "rainbow"
  | "drizzly"
  | "stormy"
  | "foggy";

export type CategoryType = "breakfast" | "lunch" | "dinner" | "snack";

export interface WeatherStats {
  weather: WeatherType;
  count: number;
}

export interface TagCategories {
  categories: string[];
}
