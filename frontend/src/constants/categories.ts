import type { CategoryType } from "../types/recipe";

export interface CategoryConfig {
  type: CategoryType;
  emoji: string;
  label: string;
}

export const CATEGORIES: CategoryConfig[] = [
  { type: "breakfast", emoji: "🍳", label: "Breakfast" },
  { type: "lunch", emoji: "🥪", label: "Lunch" },
  { type: "dinner", emoji: "🍽️", label: "Dinner" },
  { type: "snack", emoji: "🍿", label: "Snack" },
];
