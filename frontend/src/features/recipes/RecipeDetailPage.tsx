import { useParams, Link } from "react-router";
import { ArrowLeft, Lightbulb } from "lucide-react";
import { useRecipeDetail } from "./useRecipeDetail";
import { RecipeIngredients } from "./RecipeIngredients";
import { RecipeSteps } from "./RecipeSteps";
import { FavoriteButton } from "../favorites/FavoriteButton";
import { Spinner } from "../../components/ui/Spinner";
import { Badge } from "../../components/ui/Badge";
import { WEATHER_MAP } from "../../constants/weather";
import { CATEGORIES } from "../../constants/categories";
import type { WeatherType } from "../../types/recipe";

export default function RecipeDetailPage() {
  const { weather, id } = useParams<{ weather: string; id: string }>();
  const { data: recipe, isLoading } = useRecipeDetail(id);
  const weatherConfig = weather ? WEATHER_MAP[weather as WeatherType] : null;

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!recipe) {
    return <div className="py-12 text-center text-text-muted">Recipe not found</div>;
  }

  const categoryConfig = CATEGORIES.find((c) => c.type === recipe.category);

  return (
    <div className="mx-auto max-w-2xl">
      <Link
        to={`/recipes/${weather}`}
        className="mb-4 inline-flex items-center gap-1 text-sm text-text-muted hover:text-primary"
      >
        <ArrowLeft size={16} /> Back to {weatherConfig?.label ?? "recipes"}
      </Link>

      <div className="mb-6 text-center">
        <span className="text-6xl">{recipe.emoji}</span>
        <div className="mt-4 flex items-center justify-center gap-3">
          <h1 className="text-3xl font-bold text-text">{recipe.name}</h1>
          <FavoriteButton recipeId={recipe.id} size={28} />
        </div>
        <p className="mt-2 text-lg text-text-muted">{recipe.why}</p>
        <div className="mt-3 flex items-center justify-center gap-2">
          <Badge variant="secondary">Serves {recipe.serves}</Badge>
          {categoryConfig && (
            <Badge>
              {categoryConfig.emoji} {categoryConfig.label}
            </Badge>
          )}
          {weatherConfig && (
            <Badge variant="primary">
              {weatherConfig.emoji} {weatherConfig.label}
            </Badge>
          )}
        </div>
      </div>

      <div className="space-y-8">
        <RecipeIngredients ingredients={recipe.ingredients} />
        <RecipeSteps steps={recipe.steps} />

        {recipe.tip && (
          <div className="flex gap-3 rounded-xl bg-accent/20 p-4">
            <Lightbulb size={20} className="mt-0.5 shrink-0 text-warning" />
            <div>
              <h3 className="font-semibold text-text">Tip</h3>
              <p className="text-sm text-text-muted">{recipe.tip}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
