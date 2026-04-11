"use client";
import { useEffect, useState, ReactNode } from "react";
import { initAuth } from "@/lib/api";

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="mt-4 text-gray-500">Loading...</p>
      </div>
    </div>
  );
}

function ErrorScreen({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md p-8">
        <h2 className="text-xl font-bold text-gray-900">Something went wrong</h2>
        <p className="mt-2 text-gray-500">{error.message || "An unexpected error occurred"}</p>
        <button
          onClick={reset}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

export default function ClientLayout({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    initAuth();
    setMounted(true);
  }, []);

  useEffect(() => {
    const handleError = (e: ErrorEvent) => {
      console.error("Global error:", e.error);
      setHasError(true);
      setError(new Error(e.message));
    };
    window.addEventListener("error", handleError);
    return () => window.removeEventListener("error", handleError);
  }, []);

  const handleReset = () => {
    setHasError(false);
    setError(null);
  };

  if (!mounted) return <LoadingScreen />;
  if (hasError && error) return <ErrorScreen error={error} reset={handleReset} />;

  return <>{children}</>;
}