import LegalPage from "@/components/LegalPage";

export default function RiskDisclosurePage() {
  return (
    <LegalPage title="Risk disclosure">
      <p>DRAFT: have this reviewed by a qualified lawyer before public launch.</p>
      <p>
        Trading binary and similar options carries a high risk of loss. You can lose your entire stake on every trade.
        Past results, backtests and signals do not guarantee future results, and no feature of PulseTrade guarantees a
        profit.
      </p>
      <p>
        Only trade with money you can afford to lose. If trading is affecting your finances or wellbeing, stop and seek
        support.
      </p>
      <p>
        PulseTrade is not a broker and does not hold your money. Deposits, withdrawals and trade execution are handled
        by Deriv through your own Deriv account. During the beta, PulseTrade only connects to Deriv demo accounts with
        virtual funds.
      </p>
      <p>You must be 18 or older to use PulseTrade, and trading may be restricted or unlawful where you live.</p>
    </LegalPage>
  );
}