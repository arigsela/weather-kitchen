import type { RecipeStep } from "../../types/recipe";

interface RecipeStepsProps {
  steps: RecipeStep[];
}

export function RecipeSteps({ steps }: RecipeStepsProps) {
  const sorted = [...steps].sort((a, b) => a.step_number - b.step_number);

  return (
    <div>
      <h2 className="mb-3 text-xl font-semibold text-text">Steps</h2>
      <ol className="space-y-4">
        {sorted.map((step) => (
          <li key={step.id} className="flex gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">
              {step.step_number}
            </span>
            <p className="pt-1 text-text">{step.step_text}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
