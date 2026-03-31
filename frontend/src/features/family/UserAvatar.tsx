interface UserAvatarProps {
  emoji: string | null;
  name: string;
  isActive?: boolean;
  size?: "sm" | "md" | "lg";
  onClick?: () => void;
}

const sizeClasses = {
  sm: "h-10 w-10 text-lg",
  md: "h-14 w-14 text-2xl",
  lg: "h-20 w-20 text-4xl",
};

export function UserAvatar({ emoji, name, isActive, size = "md", onClick }: UserAvatarProps) {
  const Component = onClick ? "button" : "div";

  return (
    <Component
      onClick={onClick}
      className={`flex flex-col items-center gap-1 ${onClick ? "cursor-pointer" : ""}`}
      aria-label={onClick ? `Select ${name}` : undefined}
    >
      <div
        className={`flex items-center justify-center rounded-full bg-gray-100 transition-all ${sizeClasses[size]} ${
          isActive ? "ring-3 ring-primary ring-offset-2" : ""
        } ${onClick ? "hover:bg-gray-200" : ""}`}
      >
        {emoji || name.charAt(0).toUpperCase()}
      </div>
      <span className={`text-sm font-medium ${isActive ? "text-primary" : "text-text-muted"}`}>
        {name}
      </span>
    </Component>
  );
}
