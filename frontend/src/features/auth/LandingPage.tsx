import { useNavigate } from "react-router";
import { Button } from "../../components/ui/Button";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F7F7F7] px-4">
      <div className="w-full max-w-sm text-center">
        <span className="text-6xl">🍳</span>
        <h1 className="mt-4 text-3xl font-bold text-text">Weather Kitchen</h1>
        <p className="mt-2 text-text-muted">
          Discover weather-perfect recipes for the whole family.
        </p>

        <div className="mt-8 space-y-3">
          <Button className="w-full" onClick={() => navigate("/login")}>
            Log In
          </Button>
          <Button variant="secondary" className="w-full" onClick={() => navigate("/signup")}>
            Create Family
          </Button>
        </div>
      </div>
    </div>
  );
}
