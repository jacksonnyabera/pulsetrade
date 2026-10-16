import LegalPage from "@/components/LegalPage";

export default function TermsPage() {
  return (
    <LegalPage title="Terms of use">
      <p>DRAFT: have this reviewed by a qualified lawyer before public launch.</p>
      <p>
        PulseTrade is a trading interface and analysis tool that connects to your own Deriv account using Deriv&apos;s
        official API. PulseTrade does not hold, move or withdraw your funds, and has no ability to do so.
      </p>
      <p>
        You are responsible for your trading decisions and for complying with the laws that apply to you. You must be
        at least 18 years old.
      </p>
      <p>
        PulseTrade provides no financial advice and no guarantee of profit. Signals and analysis are informational
        only.
      </p>
      <p>
        If PulseTrade charges a fee, subscription or markup in future, it will be shown clearly before you use the
        feature or place a trade.
      </p>
      <p>You can disconnect your Deriv account and delete your PulseTrade account at any time.</p>
    </LegalPage>
  );
}