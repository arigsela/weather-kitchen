import { useState, useEffect } from "react";
import { useUserIngredients } from "./useUserIngredients";
import { useSaveIngredients } from "./useSaveIngredients";
import { IngredientCategory } from "./IngredientCategory";
import { INGREDIENT_CATEGORIES } from "../../constants/ingredients";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";

export default function PantryPage() {
  const { data: savedTags, isLoading } = useUserIngredients();
  const saveMutation = useSaveIngredients();
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (savedTags && !initialized) {
      setSelectedTags(savedTags);
      setInitialized(true);
    }
  }, [savedTags, initialized]);

  function handleToggle(tag: string) {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  }

  function handleSave() {
    saveMutation.mutate(selectedTags);
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text">My Pantry</h1>
          <p className="text-text-muted">
            {selectedTags.length} ingredient{selectedTags.length !== 1 ? "s" : ""} selected
          </p>
        </div>
        <Button onClick={handleSave} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? "Saving..." : "Save"}
        </Button>
      </div>

      <div className="space-y-4">
        {INGREDIENT_CATEGORIES.map((category) => (
          <IngredientCategory
            key={category.name}
            category={category}
            selectedTags={selectedTags}
            onToggle={handleToggle}
          />
        ))}
      </div>
    </div>
  );
}
