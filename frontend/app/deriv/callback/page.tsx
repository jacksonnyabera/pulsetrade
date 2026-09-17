"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function DerivCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"processing" | "error" | "success">("processing");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    console.log("[deriv-callback] effect started");

    const run = async () => {
      const code = searchParams.get("code");
      const returnedState = searchParams.get("state");
      const error = searchParams.get("error");

      console.log("[deriv-callback] params", { code, returnedState, error });

      if (error) {
        console.log("[deriv-callback] error param present, stopping");
        setStatus("error");
        setErrorMessage(searchParams.get("error_description") || error);
        return;
      }

      const storedState = localStorage.getItem("oauth_state");
      const codeVerifier = localStorage.getItem("pkce_code_verifier");

      console.log("[deriv-callback] local storage", { storedState, codeVerifier });

      if (!code || !returnedState || returnedState !== storedState || !codeVerifier) {
        console.log("[deriv-callback] security check failed, stopping", {
          hasCode: !!code,
          hasReturnedState: !!returnedState,
          stateMatches: returnedState === storedState,
          hasCodeVerifier: !!codeVerifier,
        });
        setStatus("error");
        setErrorMessage("Security check failed (state mismatch). Please try connecting again.");
        return;
      }

      console.log("[deriv-callback] about to fetch backend");

      try {
        const accessToken = localStorage.getItem("pulsetrade_access_token");
        console.log("[deriv-callback] access token present?", !!accessToken);

        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/deriv/callback`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
          },
          body: JSON.stringify({ code, code_verifier: codeVerifier }),
        });

        console.log("[deriv-callback] fetch resolved, status:", res.status);

        localStorage.removeItem("oauth_state");
        localStorage.removeItem("pkce_code_verifier");

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || "Failed to connect Deriv account");
        }

        setStatus("success");
        setTimeout(() => router.push("/dashboard"), 1500);
      } catch (err) {
        console.log("[deriv-callback] caught error:", err);
        setStatus("error");
        setErrorMessage(err instanceof Error ? err.message : "Something went wrong");
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
          <p className="text-neutral-400 text-sm">{errorMessage}</p>
        </>
      )}
    </main>
  );
}