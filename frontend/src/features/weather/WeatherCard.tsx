import { Link } from "react-router";
import type { WeatherConfig } from "../../constants/weather";

interface WeatherCardProps {
  config: WeatherConfig;
  count?: number;
}

export function WeatherCard({ config, count }: WeatherCardProps) {
  return (
    <Link
      to={`/recipes/${config.type}`}
      className="flex flex-col items-center gap-2 rounded-xl bg-surface p-6 shadow-sm transition-all hover:scale-105 hover:shadow-md active:scale-100"
      style={{ borderBottom: `4px solid ${config.color}` }}
    >
      <span className="text-5xl" role="img" aria-label={config.label}>
        {config.emoji}
      </span>
      <span className="text-lg font-semibold text-text">{config.label}</span>
      <span className="text-sm text-text-muted">{config.description}</span>
      {count !== undefined && (
        <span className="mt-1 rounded-full bg-gray-100 px-3 py-0.5 text-sm font-medium text-text-muted">
          {count} {count === 1 ? "recipe" : "recipes"}
        </span>
      )}
    </Link>
  );
}
