import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { IngredientChip } from "./IngredientChip";
import type { IngredientCategory as IngredientCategoryType } from "../../constants/ingredients";

interface IngredientCategoryProps {
  category: IngredientCategoryType;
  selectedTags: string[];
  onToggle: (tag: string) => void;
}

export function IngredientCategory({ category, selectedTags, onToggle }: IngredientCategoryProps) {
  const [isOpen, setIsOpen] = useState(true);
  const selectedCount = category.tags.filter((t) => selectedTags.includes(t)).length;

  return (
    <div className="rounded-xl bg-surface p-4 shadow-sm">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-2xl">{category.emoji}</span>
          <span className="text-lg font-semibold text-text">{category.name}</span>
          {selectedCount > 0 && (
            <span className="rounded-full bg-secondary/10 px-2 py-0.5 text-xs font-medium text-secondary">
              {selectedCount}
            </span>
          )}
        </div>
        {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>
      {isOpen && (
        <div className="mt-3 flex flex-wrap gap-2">
          {category.tags.map((tag) => (
            <IngredientChip
              key={tag}
              tag={tag}
              isSelected={selectedTags.includes(tag)}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  );
}
