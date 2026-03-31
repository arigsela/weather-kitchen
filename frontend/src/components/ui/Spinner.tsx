interface SpinnerProps {
  fullScreen?: boolean;
  size?: "sm" | "md" | "lg";
}

export function Spinner({ fullScreen, size = "md" }: SpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  const spinner = (
    <div
      className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-primary/30 border-t-primary`}
      role="status"
      aria-label="Loading"
    />
  );

  if (fullScreen) {
    return <div className="flex h-screen w-screen items-center justify-center">{spinner}</div>;
  }

  return spinner;
}
