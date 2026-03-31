import { useState } from "react";
import { useParams, Link } from "react-router";
import { ArrowLeft } from "lucide-react";
import { useRecipes } from "./useRecipes";
import { RecipeGrid } from "./RecipeGrid";
import { CategoryFilter } from "./CategoryFilter";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import { Pagination } from "../../components/ui/Pagination";
import { WEATHER_MAP } from "../../constants/weather";
import type { WeatherType, CategoryType } from "../../types/recipe";

export default function RecipeListPage() {
  const { weather } = useParams<{ weather: string }>();
  const [category, setCategory] = useState<CategoryType | null>(null);
  const [page, setPage] = useState(1);

  const weatherConfig = weather ? WEATHER_MAP[weather as WeatherType] : null;

  const { data, isLoading } = useRecipes({
    weather: weather as WeatherType,
    category: category ?? undefined,
    page,
    limit: 12,
  });

  return (
    <div>
      <div className="mb-6">
        <Link
          to="/home"
          className="mb-2 inline-flex items-center gap-1 text-sm text-text-muted hover:text-primary"
        >
          <ArrowLeft size={16} /> Back to weather
        </Link>
        {weatherConfig && (
          <h1 className="text-2xl font-bold text-text">
            {weatherConfig.emoji} {weatherConfig.label} Recipes
          </h1>
        )}
      </div>

      <div className="mb-6">
        <CategoryFilter
          selected={category}
          onChange={(c) => {
            setCategory(c);
            setPage(1);
          }}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : !data?.items.length ? (
        <EmptyState
          emoji="🔍"
          title="No recipes found"
          description="Try a different category or weather type"
        />
      ) : (
        <>
          <RecipeGrid recipes={data.items} />
          <Pagination page={page} totalPages={data.pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
