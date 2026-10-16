export default function LegalPage({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-neutral-950 text-white px-4 py-10">
      <article className="max-w-2xl mx-auto flex flex-col gap-4 text-neutral-300">
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {children}
        <a href="/" className="text-emerald-400 hover:underline mt-6">
          ← Back
        </a>
      </article>
    </main>
  );
}