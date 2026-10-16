import LegalPage from "@/components/LegalPage";

export default function PrivacyPage() {
  return (
    <LegalPage title="Privacy policy">
      <p>DRAFT: have this reviewed by a qualified lawyer before public launch.</p>
      <p>We store: your email and name, a hashed (never plain) password, and your login history (time, IP address and device).</p>
      <p>
        When you connect Deriv we store your Deriv account ID and currency, and an encrypted access token. We never see
        your Deriv password.
      </p>
      <p>You can disconnect Deriv or ask us to delete your account and data at any time.</p>
      <p>We do not sell your personal data.</p>
    </LegalPage>
  );
}