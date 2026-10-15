"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch } from "@/lib/api";

function DerivCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"processing" | "error" | "success">("processing");
  const [errorMessage, setErrorMessage] = useState("");
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const run = async () => {
      const code = searchParams.get("code");
      const returnedState = searchParams.get("state");
      const error = searchParams.get("error");

      if (error) {
        setStatus("error");
        setErrorMessage(searchParams.get("error_description") || error);
        return;
      }

      const storedState = localStorage.getItem("oauth_state");
      const codeVerifier = localStorage.getItem("pkce_code_verifier");

      if (!code || !returnedState || returnedState !== storedState || !codeVerifier) {
        setStatus("error");
        setErrorMessage("Security check failed (state mismatch). Please try connecting again.");
        return;
      }

      try {
        await apiFetch("/api/v1/deriv/callback", {
          method: "POST",
          body: JSON.stringify({ code, code_verifier: codeVerifier }),
        });
        setStatus("success");
        setTimeout(() => router.push("/trade"), 1500);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Something went wrong";
        setStatus("error");
        setErrorMessage(
          message.toLowerCase().includes("validate credentials")
            ? "Your PulseTrade session expired. Log in again, then click Connect Deriv."
            : message
        );
      } finally {
        localStorage.removeItem("oauth_state");
        localStorage.removeItem("pkce_code_verifier");
      }
    };

    run();
  }, [searchParams, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-white gap-4">
      {status === "processing" && <p>Connecting your Deriv account...</p>}
      {status === "success" && <p className="text-emerald-400">Connected! Redirecting...</p>}
      {status === "error" && (
        <>
          <p className="text-red-400">Connection failed</p>
          <p className="text-neutral-400 text-sm max-w-md text-center">{errorMessage}</p>
          <a href="/login" className="text-emerald-400 hover:underline">
            Back to login
          </a>
        </>
      )}
    </main>
  );
}

export default function DerivCallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-white">
          <p>Loading...</p>
        </main>
      }
    >
      <DerivCallbackInner />
    </Suspense>
  );
}