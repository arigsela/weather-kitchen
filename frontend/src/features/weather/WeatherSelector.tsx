import { WEATHER_TYPES } from "../../constants/weather";
import { useWeatherStats } from "./useWeatherStats";
import { WeatherCard } from "./WeatherCard";
import { Spinner } from "../../components/ui/Spinner";

export default function WeatherSelector() {
  const { data: stats, isLoading } = useWeatherStats();

  const statsMap = new Map(stats?.map((s) => [s.weather, s.count]));

  return (
    <div>
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-text">What's the weather like?</h1>
        <p className="mt-2 text-lg text-text-muted">Pick the weather to find the perfect meal</p>
      </div>
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {WEATHER_TYPES.map((config) => (
            <WeatherCard key={config.type} config={config} count={statsMap.get(config.type)} />
          ))}
        </div>
      )}
    </div>
  );
}
