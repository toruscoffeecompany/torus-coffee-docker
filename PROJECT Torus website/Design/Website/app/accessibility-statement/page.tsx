import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Accessibility Statement",
  description: "Accessibility Statement for Torus Coffee Company.",
};

export default function PolicyPage() {
  return (
    <section className="mx-auto max-w-4xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Policy</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Accessibility Statement</h1>
      <div className="mt-8 rounded-lg border border-midnight/10 bg-white p-6 text-lg leading-8 text-ink/75">
        <p>This placeholder must be replaced with updated 2026 accessibility language before launch and matched to the final website accessibility practices.</p>
      </div>
    </section>
  );
}
