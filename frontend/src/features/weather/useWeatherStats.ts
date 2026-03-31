import { useQuery } from "@tanstack/react-query";
import { fetchWeatherStats } from "../../api/recipes";

export function useWeatherStats() {
  return useQuery({
    queryKey: ["weather-stats"],
    queryFn: fetchWeatherStats,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
