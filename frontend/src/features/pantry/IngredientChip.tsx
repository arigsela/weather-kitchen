interface IngredientChipProps {
  tag: string;
  isSelected: boolean;
  onToggle: (tag: string) => void;
}

export function IngredientChip({ tag, isSelected, onToggle }: IngredientChipProps) {
  return (
    <button
      type="button"
      onClick={() => onToggle(tag)}
      className={`min-h-[44px] rounded-full px-4 py-2 text-sm font-medium capitalize transition-all ${
        isSelected
          ? "bg-secondary text-white shadow-sm"
          : "bg-gray-100 text-text-muted hover:bg-gray-200"
      }`}
      aria-pressed={isSelected}
    >
      {tag}
    </button>
  );
}
