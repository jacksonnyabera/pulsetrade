"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("pulsetrade_access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    apiFetch("/api/v1/auth/me")
      .then(setUser)
      .catch(() => router.push("/login"));
  }, [router]);

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-neutral-950 text-white">
        <p>Loading...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-white gap-4">
      <h1 className="text-2xl font-bold">Welcome, {user.email}</h1>
      <p className="text-neutral-400">Role: {user.role}</p>
      <a href="/deriv/connect" className="text-emerald-400 hover:underline">
        Connect your Deriv account →
      </a>
    </main>
  );
}