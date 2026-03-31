import { Link } from "react-router";

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-4 text-center text-sm text-text-muted">
      <div className="mx-auto max-w-[1200px] px-4">
        <Link to="/privacy" className="hover:text-primary hover:underline">
          Privacy Policy
        </Link>
        <span className="mx-2">·</span>
        <span>Weather Kitchen</span>
      </div>
    </footer>
  );
}
