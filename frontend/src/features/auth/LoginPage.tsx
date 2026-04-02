import { useState } from "react";
import { useNavigate, Link } from "react-router";
import { login } from "../../api/auth";
import { useAppStore } from "../../store/appStore";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";
import { Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const navigate = useNavigate();
  const { setTokens, setCurrentFamily, setSetupComplete } = useAppStore();

  const [familyName, setFamilyName] = useState("");
  const [password, setPassword] = useState("");
  const [betaCode, setBetaCode] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res = await login({
        name: familyName,
        password,
        ...(betaCode && { beta_code: betaCode }),
      });
      setTokens(res.access_token, res.refresh_token, res.expires_in);
      setCurrentFamily(res.id);
      setSetupComplete();
      navigate("/home");
    } catch {
      setError("Invalid family name or password. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F7F7F7] px-4">
      <div className="w-full max-w-md rounded-xl bg-surface p-8 shadow-lg">
        <div className="mb-6 text-center">
          <span className="text-5xl">🍳</span>
          <h1 className="mt-3 text-2xl font-bold text-text">Welcome Back</h1>
          <p className="mt-1 text-text-muted">Log in to your family account</p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-danger/10 p-3 text-sm text-danger">{error}</div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="familyName" className="mb-1 block text-sm font-medium text-text">
              Username
            </label>
            <input
              id="familyName"
              type="text"
              required
              value={familyName}
              onChange={(e) => setFamilyName(e.target.value.replace(/\s/g, ""))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="smith_family"
              autoFocus
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-text">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2.5 pr-10 text-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="Your password"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="betaCode" className="mb-1 block text-sm font-medium text-text">
              Beta Access Code
            </label>
            <input
              id="betaCode"
              type="text"
              value={betaCode}
              onChange={(e) => setBetaCode(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="Enter beta code"
            />
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? <Spinner size="sm" /> : "Log In"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-text-muted">
          New here?{" "}
          <Link to="/signup" className="font-medium text-primary hover:underline">
            Create a family account
          </Link>
        </p>
      </div>
    </div>
  );
}
