import { useState } from "react";
import { useNavigate, Link } from "react-router";
import { createFamily } from "../../api/families";
import { createUser } from "../../api/users";
import { useAppStore } from "../../store/appStore";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";
import { Eye, EyeOff } from "lucide-react";

type Step = "family" | "user";

const EMOJI_OPTIONS = [
  "😊",
  "😎",
  "🤩",
  "🥳",
  "😋",
  "🧒",
  "👦",
  "👧",
  "👨",
  "👩",
  "👴",
  "👵",
  "🐱",
];

export default function FamilySetupPage() {
  const navigate = useNavigate();
  const { setTokens, setCurrentFamily, setCurrentUser, setSetupComplete, accessToken } =
    useAppStore();

  const [step, setStep] = useState<Step>(accessToken ? "user" : "family");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Family form
  const [familyName, setFamilyName] = useState("");
  const [familySize, setFamilySize] = useState(4);
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // User form
  const [userName, setUserName] = useState("");
  const [selectedEmoji, setSelectedEmoji] = useState(EMOJI_OPTIONS[0]);

  async function handleCreateFamily(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res = await createFamily({
        name: familyName,
        family_size: familySize,
        password,
      });
      setTokens(res.access_token, res.refresh_token, res.expires_in);
      setCurrentFamily(res.id);
      setStep("user");
    } catch {
      setError("Failed to create family. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateUser(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const user = await createUser({
        name: userName,
        emoji: selectedEmoji,
      });
      setCurrentUser(user.id);
      setSetupComplete();
      navigate("/home");
    } catch (err) {
      console.error("Create user error:", err);
      setError("Failed to create user. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F7F7F7] px-4">
      <div className="w-full max-w-md rounded-xl bg-surface p-8 shadow-lg">
        <div className="mb-6 text-center">
          <span className="text-5xl">🍳</span>
          <h1 className="mt-3 text-2xl font-bold text-text">Weather Kitchen</h1>
          <p className="mt-1 text-text-muted">
            {step === "family" ? "Set up your family" : "Who's cooking today?"}
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-danger/10 p-3 text-sm text-danger">{error}</div>
        )}

        {step === "family" ? (
          <>
            <form onSubmit={handleCreateFamily} className="space-y-4">
              <div>
                <label htmlFor="familyName" className="mb-1 block text-sm font-medium text-text">
                  Username
                </label>
                <input
                  id="familyName"
                  type="text"
                  required
                  minLength={3}
                  maxLength={30}
                  value={familyName}
                  onChange={(e) => setFamilyName(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ""))}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  placeholder="smith_family"
                />
                <p className="mt-1 text-xs text-text-muted">
                  Letters, numbers, underscores and hyphens only. No spaces.
                </p>
              </div>

              <div>
                <label htmlFor="familySize" className="mb-1 block text-sm font-medium text-text">
                  Family Size: {familySize}
                </label>
                <input
                  id="familySize"
                  type="range"
                  min={1}
                  max={20}
                  value={familySize}
                  onChange={(e) => setFamilySize(Number(e.target.value))}
                  className="w-full accent-primary"
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
                    minLength={8}
                    maxLength={128}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2.5 pr-10 text-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                    placeholder="Min 8 chars, upper, lower, number"
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
                <p className="mt-1 text-xs text-text-muted">
                  At least 8 characters with uppercase, lowercase, and a number.
                </p>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? <Spinner size="sm" /> : "Create Family"}
              </Button>
            </form>

            <p className="mt-4 text-center text-sm text-text-muted">
              Already have an account?{" "}
              <Link to="/login" className="font-medium text-primary hover:underline">
                Log in
              </Link>
            </p>
          </>
        ) : (
          <form onSubmit={handleCreateUser} className="space-y-4">
            <div>
              <label htmlFor="userName" className="mb-1 block text-sm font-medium text-text">
                Your Name
              </label>
              <input
                id="userName"
                type="text"
                required
                minLength={1}
                maxLength={50}
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="Chef Alex"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-text">Pick Your Avatar</label>
              <div className="flex flex-wrap gap-2">
                {EMOJI_OPTIONS.map((emoji) => (
                  <button
                    key={emoji}
                    type="button"
                    onClick={() => setSelectedEmoji(emoji)}
                    className={`flex h-12 w-12 items-center justify-center rounded-lg text-2xl transition-all ${
                      selectedEmoji === emoji
                        ? "bg-primary/10 ring-2 ring-primary"
                        : "bg-gray-100 hover:bg-gray-200"
                    }`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? <Spinner size="sm" /> : "Start Cooking!"}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
