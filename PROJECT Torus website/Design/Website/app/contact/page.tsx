import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact",
  description: "Contact Torus Coffee Company for order questions, wholesale inquiries, custom orders, and website support.",
};

export default function ContactPage() {
  return (
    <section className="mx-auto max-w-5xl px-5 py-14">
      <p className="text-sm font-bold uppercase tracking-[0.16em] text-berry">Contact</p>
      <h1 className="mt-3 font-display text-5xl font-bold text-midnight">Send a signal.</h1>
      <p className="mt-6 text-lg leading-8 text-ink/75">
        Use this page for order questions, wholesale inquiries, custom order ideas, and website issue reports. A secure form will be wired in after the email/contact service decision.
      </p>
      <div className="mt-8 rounded-lg border border-midnight/10 bg-white p-6">
        <p className="font-bold text-midnight">Current public contact info to confirm before launch:</p>
        <ul className="mt-4 grid gap-2 text-ink/75">
          <li>Email: admin@toruscoffeecompany.com</li>
          <li>Phone: (319) 383-1280 (cell) / (319) 519-2539 (home)</li>
          <li>Location: Iowa / Iowa City area</li>
        </ul>
      </div>
    </section>
  );
}
