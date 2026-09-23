"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { generateCodeChallenge, generateCodeVerifier, generateState } from "@/lib/pkce";

export default function ConnectDerivPage() {
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem("pulsetrade_access_token")) {
      router.push("/login");
    }
  }, [router]);

  const handleConnect = async () => {
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);
    const state = generateState();

    localStorage.setItem("pkce_code_verifier", codeVerifier);
    localStorage.setItem("oauth_state", state);

    const params = new URLSearchParams({
      response_type: "code",
      client_id: process.env.NEXT_PUBLIC_DERIV_CLIENT_ID!,
      redirect_uri: process.env.NEXT_PUBLIC_DERIV_REDIRECT_URI!,
      scope: "trade account_manage application_read",
      state,
      code_challenge: codeChallenge,
      code_challenge_method: "S256",
    });

    window.location.href = `${process.env.NEXT_PUBLIC_DERIV_AUTH_URL}?${params.toString()}`;
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-white gap-4">
      <h1 className="text-2xl font-bold">Connect your Deriv account</h1>
      <p className="text-neutral-400 max-w-md text-center">
        PulseTrade never sees your Deriv password. You&apos;ll be redirected to Deriv to log in and
        authorize this connection.
      </p>
      <button
        onClick={handleConnect}
        className="bg-emerald-500 hover:bg-emerald-600 text-black font-semibold px-6 py-3 rounded-lg"
      >
        Connect Deriv
      </button>
    </main>
  );
}