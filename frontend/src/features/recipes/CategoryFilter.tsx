import { CATEGORIES } from "../../constants/categories";
import type { CategoryType } from "../../types/recipe";

interface CategoryFilterProps {
  selected: CategoryType | null;
  onChange: (category: CategoryType | null) => void;
}

export function CategoryFilter({ selected, onChange }: CategoryFilterProps) {
  return (
    <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filter by category">
      <button
        role="tab"
        aria-selected={selected === null}
        onClick={() => onChange(null)}
        className={`min-h-[44px] rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
          selected === null
            ? "bg-primary text-white"
            : "bg-gray-100 text-text-muted hover:bg-gray-200"
        }`}
      >
        All
      </button>
      {CATEGORIES.map((cat) => (
        <button
          key={cat.type}
          role="tab"
          aria-selected={selected === cat.type}
          onClick={() => onChange(cat.type)}
          className={`min-h-[44px] rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selected === cat.type
              ? "bg-primary text-white"
              : "bg-gray-100 text-text-muted hover:bg-gray-200"
          }`}
        >
          {cat.emoji} {cat.label}
        </button>
      ))}
    </div>
  );
}
