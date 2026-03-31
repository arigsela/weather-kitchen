import type { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export function Card({ hoverable, className = "", children, ...props }: CardProps) {
  return (
    <div
      className={`rounded-xl bg-surface p-6 shadow-sm ${
        hoverable ? "cursor-pointer transition-shadow hover:shadow-md" : ""
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
