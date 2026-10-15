"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ColorType, LineSeries, createChart, type ISeriesApi, type UTCTimestamp } from "lightweight-charts";
import { apiFetch } from "@/lib/api";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Msg = Record<string, any>;
type Side = "CALL" | "PUT";
type Quote = { payout: number; ask: number } | null;
type Trade = {
  contractId: number;
  side: Side;
  symbol: string;
  stake: number;
  status: "open" | "won" | "lost";
  profit?: number;
};

const SYMBOLS = ["1HZ100V", "R_100", "R_50"];

export default function TradePage() {
  const router = useRouter();
  const wsRef = useRef<WebSocket | null>(null);
  const reqId = useRef(1);
  const pending = useRef(new Map<number, { resolve: (m: Msg) => void; reject: (e: Error) => void }>());
  const chartEl = useRef<HTMLDivElement | null>(null);
  const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const lastTime = useRef(0);
  const symbolRef = useRef("1HZ100V");

  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");
  const [balance, setBalance] = useState<number | null>(null);
  const [currency, setCurrency] = useState<string | null>(null);
  const [price, setPrice] = useState<number | null>(null);
  const [symbol, setSymbol] = useState("1HZ100V");
  const [stake, setStake] = useState(1);
  const [duration, setDuration] = useState(5);
  const [unit, setUnit] = useState<"t" | "s" | "m">("t");
  const [quotes, setQuotes] = useState<{ CALL: Quote; PUT: Quote }>({ CALL: null, PUT: null });
  const [trades, setTrades] = useState<Trade[]>([]);
  const [busy, setBusy] = useState(false);

  const send = (payload: Msg) =>
    new Promise<Msg>((resolve, reject) => {
      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        reject(new Error("Not connected"));
        return;
      }
      const id = reqId.current++;
      pending.current.set(id, { resolve, reject });
      ws.send(JSON.stringify({ ...payload, req_id: id }));
    });

  // Chart (always mounted so the container exists)
  useEffect(() => {
    if (!chartEl.current) return;
    const chart = createChart(chartEl.current, {
      layout: { background: { type: ColorType.Solid, color: "#0a0a0a" }, textColor: "#a3a3a3" },
      grid: { vertLines: { color: "#171717" }, horzLines: { color: "#171717" } },
      timeScale: { timeVisible: true, secondsVisible: true },
      autoSize: true,
    });
    seriesRef.current = chart.addSeries(LineSeries, { color: "#10b981", lineWidth: 2 });
    return () => {
      chart.remove();
      seriesRef.current = null;
    };
  }, []);

  // Connect: backend gives a short-lived demo WebSocket URL, browser connects to Deriv directly
  useEffect(() => {
    if (!localStorage.getItem("pulsetrade_access_token")) {
      router.push("/login");
      return;
    }
    let cancelled = false;
    let ws: WebSocket | null = null;
    const waiting = pending.current;

    (async () => {
      try {
        const { url } = await apiFetch("/api/v1/deriv/ws-url", { method: "POST", body: "{}" });
        if (cancelled) return;
        ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          setConnected(true);
          send({ balance: 1, subscribe: 1 }).catch((e) => setError(e.message));
        };
        ws.onclose = () => setConnected(false);
        ws.onerror = () => setError("Connection to Deriv failed. Reconnect your Deriv account and reload.");

        ws.onmessage = (event) => {
          const msg: Msg = JSON.parse(event.data);

          const p = typeof msg.req_id === "number" ? waiting.get(msg.req_id) : undefined;
          if (p) {
            waiting.delete(msg.req_id);
            if (msg.error) p.reject(new Error(msg.error.message ?? "Request failed"));
            else p.resolve(msg);
          } else if (msg.error) {
            setError(msg.error.message ?? "Request failed");
          }

          if (msg.msg_type === "balance" && msg.balance) {
            setBalance(Number(msg.balance.balance));
            setCurrency(String(msg.balance.currency));
          }

          if (msg.msg_type === "tick" && msg.tick) {
            const tickSymbol = msg.tick.underlying_symbol ?? msg.tick.symbol;
            if (tickSymbol && tickSymbol !== symbolRef.current) return;
            const t = Number(msg.tick.epoch);
            const value = Number(msg.tick.quote);
            setPrice(value);
            if (t >= lastTime.current && seriesRef.current) {
              lastTime.current = t;
              seriesRef.current.update({ time: t as UTCTimestamp, value });
            }
          }

          if (msg.msg_type === "proposal_open_contract" && msg.proposal_open_contract) {
            const poc = msg.proposal_open_contract;
            if (poc.is_sold) {
              const profit = Number(poc.profit);
              setTrades((prev) =>
                prev.map((t) =>
                  t.contractId === Number(poc.contract_id)
                    ? { ...t, status: profit >= 0 ? "won" : "lost", profit }
                    : t
                )
              );
              if (msg.subscription?.id) ws?.send(JSON.stringify({ forget: msg.subscription.id }));
            }
          }
        };
      } catch (e) {
        setError(e instanceof Error ? e.message : "Could not connect");
      }
    })();

    return () => {
      cancelled = true;
      ws?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  // Tick subscription follows the selected symbol
  useEffect(() => {
    if (!connected) return;
    symbolRef.current = symbol;
    lastTime.current = 0;
    seriesRef.current?.setData([]);
    setPrice(null);
    send({ forget_all: "ticks" }).catch(() => {});
    send({ ticks: symbol, subscribe: 1 }).catch((e) => setError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connected, symbol]);

  // Payout quotes for both buttons, refreshed when inputs change
  useEffect(() => {
    if (!connected || !currency) return;
    const handle = setTimeout(async () => {
      const ask = async (side: Side): Promise<Quote> => {
        try {
          const r = await send({
            proposal: 1,
            amount: stake,
            basis: "stake",
            contract_type: side,
            currency,
            duration,
            duration_unit: unit,
            underlying_symbol: symbol,
          });
          return { ask: Number(r.proposal.ask_price), payout: Number(r.proposal.payout) };
        } catch (e) {
          setError(e instanceof Error ? e.message : "Quote failed");
          return null;
        }
      };
      setError("");
      const [call, put] = await Promise.all([ask("CALL"), ask("PUT")]);
      setQuotes({ CALL: call, PUT: put });
    }, 500);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connected, currency, symbol, stake, duration, unit]);

  const placeTrade = async (side: Side) => {
    if (!currency) return;
    setBusy(true);
    setError("");
    try {
      const proposal = await send({
        proposal: 1,
        amount: stake,
        basis: "stake",
        contract_type: side,
        currency,
        duration,
        duration_unit: unit,
        underlying_symbol: symbol,
      });
      const bought = await send({
        buy: proposal.proposal.id,
        price: Number(proposal.proposal.ask_price),
      });
      const contractId = Number(bought.buy.contract_id);
      setTrades((prev) => [{ contractId, side, symbol, stake, status: "open" }, ...prev]);
      send({ proposal_open_contract: 1, contract_id: contractId, subscribe: 1 }).catch((e) => setError(e.message));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Trade failed");
    } finally {
      setBusy(false);
    }
  };

  const ready = connected && currency !== null && !busy;
  const inputClass = "bg-neutral-900 border border-neutral-800 rounded-lg px-3 py-2 outline-none focus:border-emerald-500";

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-4 md:p-6">
      <div className="max-w-5xl mx-auto flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-xl font-bold">Trade (demo account)</h1>
          <div className="text-sm text-neutral-400">
            {connected ? "Connected" : "Connecting..."}
            {balance !== null && currency && (
              <span className="ml-3 text-white font-semibold">
                Balance: {balance.toFixed(2)} {currency}
              </span>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="md:col-span-2 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <select value={symbol} onChange={(e) => setSymbol(e.target.value)} className={inputClass}>
                {SYMBOLS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <span className="text-3xl font-mono">{price !== null ? price : "--"}</span>
            </div>
            <div ref={chartEl} className="h-72 w-full rounded-lg overflow-hidden border border-neutral-800" />
          </div>

          <div className="flex flex-col gap-3 bg-neutral-900 border border-neutral-800 rounded-lg p-4">
            <label className="text-sm text-neutral-400">
              Stake ({currency ?? "..."})
              <input
                type="number"
                min={0.35}
                step={0.5}
                value={stake}
                onChange={(e) => setStake(Number(e.target.value))}
                className={`${inputClass} w-full mt-1`}
              />
            </label>
            <div className="flex gap-2">
              <label className="text-sm text-neutral-400 flex-1">
                Duration
                <input
                  type="number"
                  min={1}
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className={`${inputClass} w-full mt-1`}
                />
              </label>
              <label className="text-sm text-neutral-400 flex-1">
                Unit
                <select
                  value={unit}
                  onChange={(e) => setUnit(e.target.value as "t" | "s" | "m")}
                  className={`${inputClass} w-full mt-1`}
                >
                  <option value="t">Ticks</option>
                  <option value="s">Seconds</option>
                  <option value="m">Minutes</option>
                </select>
              </label>
            </div>

            <button
              onClick={() => placeTrade("CALL")}
              disabled={!ready}
              className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-black font-bold py-4 rounded-lg"
            >
              Rise / Higher
              <div className="text-xs font-normal">
                {quotes.CALL ? `Payout ${quotes.CALL.payout.toFixed(2)} | Risk ${stake.toFixed(2)}` : "Getting price..."}
              </div>
            </button>
            <button
              onClick={() => placeTrade("PUT")}
              disabled={!ready}
              className="bg-red-500 hover:bg-red-600 disabled:opacity-40 text-white font-bold py-4 rounded-lg"
            >
              Fall / Lower
              <div className="text-xs font-normal">
                {quotes.PUT ? `Payout ${quotes.PUT.payout.toFixed(2)} | Risk ${stake.toFixed(2)}` : "Getting price..."}
              </div>
            </button>

            {error && <p className="text-red-400 text-sm">{error}</p>}
            <p className="text-xs text-neutral-500">
              Demo account with virtual funds. Trading involves risk and you can lose your entire stake. No outcome is
              guaranteed.
            </p>
          </div>
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
          <h2 className="font-semibold mb-2">This session</h2>
          {trades.length === 0 ? (
            <p className="text-neutral-500 text-sm">No trades yet.</p>
          ) : (
            <ul className="text-sm divide-y divide-neutral-800">
              {trades.map((t) => (
                <li key={t.contractId} className="py-2 flex justify-between">
                  <span>
                    {t.side === "CALL" ? "Rise" : "Fall"} {t.symbol} | stake {t.stake}
                  </span>
                  <span
                    className={
                      t.status === "won" ? "text-emerald-400" : t.status === "lost" ? "text-red-400" : "text-neutral-400"
                    }
                  >
                    {t.status === "open" ? "open" : `${t.status} ${t.profit?.toFixed(2)}`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </main>
  );
}