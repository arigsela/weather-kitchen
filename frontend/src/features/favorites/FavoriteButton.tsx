import { Heart } from "lucide-react";
import { useFavorites } from "./useFavorites";
import { useToggleFavorite } from "./useToggleFavorite";

interface FavoriteButtonProps {
  recipeId: string;
  size?: number;
}

export function FavoriteButton({ recipeId, size = 24 }: FavoriteButtonProps) {
  const { data: favorites = [] } = useFavorites();
  const { mutate } = useToggleFavorite();
  const isFavorite = favorites.some((r) => r.recipe_id === recipeId);

  return (
    <button
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        mutate({ recipeId, isFavorite });
      }}
      className={`flex min-h-[44px] min-w-[44px] items-center justify-center rounded-full transition-all ${
        isFavorite ? "text-danger" : "text-gray-300 hover:text-danger/60"
      }`}
      aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
      aria-pressed={isFavorite}
    >
      <Heart
        size={size}
        fill={isFavorite ? "currentColor" : "none"}
        className="transition-transform active:scale-90"
      />
    </button>
  );
}
