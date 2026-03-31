import type { WeatherType } from "../types/recipe";

export interface WeatherConfig {
  type: WeatherType;
  emoji: string;
  label: string;
  description: string;
  color: string;
}

export const WEATHER_TYPES: WeatherConfig[] = [
  {
    type: "sunny",
    emoji: "☀️",
    label: "Sunny",
    description: "Bright and warm",
    color: "var(--color-weather-sunny)",
  },
  {
    type: "rainy",
    emoji: "🌧️",
    label: "Rainy",
    description: "Wet and cozy",
    color: "var(--color-weather-rainy)",
  },
  {
    type: "snowy",
    emoji: "❄️",
    label: "Snowy",
    description: "Cold and magical",
    color: "var(--color-weather-snowy)",
  },
  {
    type: "hot",
    emoji: "🔥",
    label: "Hot",
    description: "Sizzling heat",
    color: "var(--color-weather-hot)",
  },
  {
    type: "windy",
    emoji: "💨",
    label: "Windy",
    description: "Breezy day",
    color: "var(--color-weather-windy)",
  },
  {
    type: "cloudy",
    emoji: "☁️",
    label: "Cloudy",
    description: "Gray skies",
    color: "var(--color-weather-cloudy)",
  },
  {
    type: "rainbow",
    emoji: "🌈",
    label: "Rainbow",
    description: "Colorful and fun",
    color: "#FF6B6B",
  },
  {
    type: "drizzly",
    emoji: "🌦️",
    label: "Drizzly",
    description: "Light rain",
    color: "var(--color-weather-drizzly)",
  },
  {
    type: "stormy",
    emoji: "⛈️",
    label: "Stormy",
    description: "Thunder and rain",
    color: "var(--color-weather-stormy)",
  },
  {
    type: "foggy",
    emoji: "🌫️",
    label: "Foggy",
    description: "Misty morning",
    color: "var(--color-weather-foggy)",
  },
];

export const WEATHER_MAP = Object.fromEntries(WEATHER_TYPES.map((w) => [w.type, w])) as Record<
  WeatherType,
  WeatherConfig
>;
