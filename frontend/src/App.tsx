import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import { useAuth } from "./hooks/useAuth";
import { Suspense, lazy } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { Spinner } from "./components/ui/Spinner";

const LandingPage = lazy(() => import("./features/auth/LandingPage"));
const LoginPage = lazy(() => import("./features/auth/LoginPage"));
const WeatherSelector = lazy(() => import("./features/weather/WeatherSelector"));
const RecipeListPage = lazy(() => import("./features/recipes/RecipeListPage"));
const RecipeDetailPage = lazy(() => import("./features/recipes/RecipeDetailPage"));
const FamilySetupPage = lazy(() => import("./features/family/FamilySetupPage"));
const UserSelectorPage = lazy(() => import("./features/family/UserSelectorPage"));
const FamilySettingsPage = lazy(() => import("./features/family/FamilySettingsPage"));
const FavoritesPage = lazy(() => import("./features/favorites/FavoritesPage"));
const PrivacyPolicyPage = lazy(() => import("./features/privacy/PrivacyPolicyPage"));
const DataManagementPage = lazy(() => import("./features/privacy/DataManagementPage"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isBootstrapping, hasCompletedSetup } = useAuth();
  if (isBootstrapping) return <Spinner fullScreen />;
  if (!isAuthenticated) return <Navigate to="/" replace />;
  if (!hasCompletedSetup) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<Spinner fullScreen />}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<FamilySetupPage />} />
            <Route path="/setup" element={<Navigate to="/signup" replace />} />
            <Route
              element={
                <AuthGuard>
                  <AppLayout />
                </AuthGuard>
              }
            >
              <Route path="/home" element={<WeatherSelector />} />
              <Route path="/recipes/:weather" element={<RecipeListPage />} />
              <Route path="/recipes/:weather/:id" element={<RecipeDetailPage />} />
              <Route path="/favorites" element={<FavoritesPage />} />
              <Route path="/users" element={<UserSelectorPage />} />
              <Route path="/settings" element={<FamilySettingsPage />} />
              <Route path="/privacy" element={<PrivacyPolicyPage />} />
              <Route path="/privacy/data" element={<DataManagementPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
