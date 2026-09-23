"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const justRegistered = searchParams.get("registered") === "true";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [needs2FA, setNeeds2FA] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          totp_code: totpCode || undefined,
        }),
      });
      localStorage.setItem("pulsetrade_access_token", data.access_token);
      localStorage.setItem("pulsetrade_refresh_token", data.refresh_token);
      router.push("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      if (message.toLowerCase().includes("2fa")) {
        setNeeds2FA(true);
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-white px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-2">Log in to PulseTrade</h1>
        {justRegistered && (
          <p className="text-emerald-400 text-sm mb-4">Account created — log in to continue.</p>
        )}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 mt-4">
          <input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-3 outline-none focus:border-emerald-500"
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-3 outline-none focus:border-emerald-500"
          />
          {needs2FA && (
            <input
              type="text"
              placeholder="6-digit 2FA code"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              className="bg-neutral-900 border border-neutral-800 rounded-lg px-4 py-3 outline-none focus:border-emerald-500"
            />
          )}
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-black font-semibold py-3 rounded-lg"
          >
            {loading ? "Logging in..." : "Log in"}
          </button>
        </form>
        <p className="text-neutral-400 text-sm mt-4">
          No account yet?{" "}
          <Link href="/register" className="text-emerald-400 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="min-h-screen bg-neutral-950" />}>
      <LoginForm />
    </Suspense>
  );
}