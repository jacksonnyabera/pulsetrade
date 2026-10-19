"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

type Trade = {
  contract_id: number;
  symbol: string;
  contract_type: string;
  stake: number;
  currency: string;
  duration: number;
  duration_unit: string;
  account_type: string;
  status: string;
  profit: number | null;
  opened_at: string;
};

export default function HistoryPage() {
  const router = useRouter();
  const [trades, setTrades] = useState<Trade[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("pulsetrade_access_token")) {
      router.push("/login");
      return;
    }
    apiFetch("/api/v1/trades")
      .then(setTrades)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load trades"));
  }, [router]);

  const closed = (trades ?? []).filter((t) => t.status !== "open");
  const wins = closed.filter((t) => t.status === "won").length;
  const losses = closed.filter((t) => t.status === "lost").length;
  const net = closed.reduce((sum, t) => sum + (t.profit ?? 0), 0);
  const winRate = wins + losses > 0 ? Math.round((wins / (wins + losses)) * 100) : 0;

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-4 md:p-6">
      <div className="max-w-4xl mx-auto flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Trade history</h1>
          <a href="/trade" className="text-emerald-400 hover:underline text-sm">
            Back to trading →
          </a>
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            ["Trades closed", String(closed.length)],
            ["Wins / losses", `${wins} / ${losses}`],
            ["Win rate", `${winRate}%`],
            ["Net profit/loss", net.toFixed(2)],
          ].map(([label, value]) => (
            <div key={label} className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
              <div className="text-xs text-neutral-400">{label}</div>
              <div className="text-lg font-semibold">{value}</div>
            </div>
          ))}
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-neutral-400 text-left">
              <tr>
                <th className="p-3">Time</th>
                <th className="p-3">Market</th>
                <th className="p-3">Type</th>
                <th className="p-3">Stake</th>
                <th className="p-3">Result</th>
                <th className="p-3">P/L</th>
              </tr>
            </thead>
            <tbody>
              {trades === null && !error && (
                <tr><td className="p-3 text-neutral-500" colSpan={6}>Loading...</td></tr>
              )}
              {trades?.length === 0 && (
                <tr><td className="p-3 text-neutral-500" colSpan={6}>No trades yet.</td></tr>
              )}
              {trades?.map((t) => (
                <tr key={t.contract_id} className="border-t border-neutral-800">
                  <td className="p-3">{new Date(t.opened_at).toLocaleString()}</td>
                  <td className="p-3">{t.symbol}</td>
                  <td className="p-3">{t.contract_type === "CALL" ? "Rise" : "Fall"}</td>
                  <td className="p-3">{t.stake.toFixed(2)} {t.currency}</td>
                  <td className={`p-3 ${t.status === "won" ? "text-emerald-400" : t.status === "lost" ? "text-red-400" : "text-neutral-400"}`}>
                    {t.status}
                  </td>
                  <td className="p-3">{t.profit !== null ? t.profit.toFixed(2) : "--"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-xs text-neutral-500">
          Demo account results. Past results do not predict future results, and trading involves a risk of loss.
        </p>
      </div>
    </main>
  );
}