"use client";
import { useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";

/**
 * Auth guard HOC — redirects to /login if no auth token is found.
 */
export default function AuthGuard({ children }: { children: ReactNode }) {
  const [checked, setChecked] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.replace("/login");
    } else {
      setChecked(true);
    }
  }, [router]);

  if (!checked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return <>{children}</>;
}
