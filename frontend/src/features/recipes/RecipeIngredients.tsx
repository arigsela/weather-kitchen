import type { RecipeIngredient } from "../../types/recipe";

interface RecipeIngredientsProps {
  ingredients: RecipeIngredient[];
}

export function RecipeIngredients({ ingredients }: RecipeIngredientsProps) {
  const sorted = [...ingredients].sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div>
      <h2 className="mb-3 text-xl font-semibold text-text">Ingredients</h2>
      <ul className="space-y-2">
        {sorted.map((ing) => (
          <li key={ing.id} className="text-text">
            {ing.ingredient_text}
          </li>
        ))}
      </ul>
    </div>
  );
}
