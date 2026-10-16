import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-white gap-6 px-4 text-center">
      <h1 className="text-4xl font-bold">PulseTrade</h1>
      <p className="text-neutral-400 max-w-md">
        A trading terminal for your own Deriv account. Beta: demo accounts only. Trading involves risk and you can
        lose your stake.
      </p>
      <div className="flex gap-3">
        <Link
          href="/login"
          className="bg-emerald-500 hover:bg-emerald-600 text-black font-semibold px-6 py-3 rounded-lg"
        >
          Log in
        </Link>
        <Link
          href="/register"
          className="border border-neutral-700 hover:border-neutral-500 px-6 py-3 rounded-lg"
        >
          Create account
        </Link>
      </div>
      <p className="text-xs text-neutral-500 flex gap-3">
        <Link href="/terms">Terms</Link>
        <Link href="/privacy">Privacy</Link>
        <Link href="/risk-disclosure">Risk disclosure</Link>
      </p>
    </main>
  );
}