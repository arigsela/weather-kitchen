import { Link } from "react-router";
import { Badge } from "../../components/ui/Badge";
import { FavoriteButton } from "../favorites/FavoriteButton";
import { CATEGORIES } from "../../constants/categories";
import type { WeatherType, CategoryType } from "../../types/recipe";

export interface RecipeListItem {
  id: string;
  name: string;
  emoji: string;
  weather: WeatherType;
  category: CategoryType;
  serves: number;
}

interface RecipeCardProps {
  recipe: RecipeListItem;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  const categoryConfig = CATEGORIES.find((c) => c.type === recipe.category);

  return (
    <div className="relative">
      <Link
        to={`/recipes/${recipe.weather}/${recipe.id}`}
        className="flex flex-col rounded-xl bg-surface p-5 shadow-sm transition-all hover:shadow-md"
      >
        <span className="text-4xl" role="img" aria-hidden="true">
          {recipe.emoji}
        </span>
        <h3 className="mt-3 text-lg font-semibold text-text line-clamp-2">{recipe.name}</h3>
        <div className="mt-auto flex items-center gap-2 pt-3">
          <Badge variant="secondary">Serves {recipe.serves}</Badge>
          {categoryConfig && (
            <Badge>
              {categoryConfig.emoji} {categoryConfig.label}
            </Badge>
          )}
        </div>
      </Link>
      <div className="absolute right-2 top-2">
        <FavoriteButton recipeId={recipe.id} size={20} />
      </div>
    </div>
  );
}
