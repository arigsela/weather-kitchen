import { Link } from "react-router";
import { useFavorites } from "./useFavorites";
import { FavoriteButton } from "./FavoriteButton";
import { ChevronRight } from "lucide-react";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import { Button } from "../../components/ui/Button";

export default function FavoritesPage() {
  const { data: favorites = [], isLoading } = useFavorites();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-text">
        My Favorites {favorites.length > 0 && `(${favorites.length})`}
      </h1>

      {favorites.length === 0 ? (
        <EmptyState
          emoji="❤️"
          title="No favorites yet!"
          description="Tap the heart on any recipe to save it here."
          action={
            <Link to="/home">
              <Button>Browse Recipes</Button>
            </Link>
          }
        />
      ) : (
        <div className="space-y-3">
          {favorites.map((fav) => (
            <div
              key={fav.id}
              className="flex items-center justify-between rounded-xl bg-surface shadow-sm"
            >
              <Link
                to={`/recipes/${fav.recipe_weather}/${fav.recipe_id}`}
                className="flex flex-1 items-center gap-3 p-4 hover:text-primary"
              >
                <span className="font-medium text-text">{fav.recipe_name}</span>
                <ChevronRight size={16} className="ml-auto shrink-0 text-text-muted" />
              </Link>
              <div className="pr-2">
                <FavoriteButton recipeId={fav.recipe_id} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
