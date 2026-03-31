import type { ReactNode } from "react";

interface EmptyStateProps {
  emoji?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ emoji = "🍳", title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <span className="text-6xl" role="img" aria-hidden="true">
        {emoji}
      </span>
      <h3 className="mt-4 text-xl font-semibold text-text">{title}</h3>
      {description && <p className="mt-2 max-w-sm text-text-muted">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
