import { Link, useLocation } from "react-router";
import { Cloud, Heart, Settings, Users } from "lucide-react";

const NAV_ITEMS = [
  { to: "/home", label: "Weather", icon: Cloud },
  { to: "/favorites", label: "Favorites", icon: Heart },
  { to: "/users", label: "Users", icon: Users },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Header() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-10 border-b border-gray-200 bg-white shadow-sm">
      <div className="mx-auto flex max-w-[1200px] items-center justify-between px-4 py-3">
        <Link to="/home" className="text-xl font-bold text-primary">
          Weather Kitchen
        </Link>
        <nav className="flex gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
            const isActive =
              location.pathname === to || (to !== "/home" && location.pathname.startsWith(to));
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-text-muted hover:bg-gray-100 hover:text-text"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon size={18} />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
