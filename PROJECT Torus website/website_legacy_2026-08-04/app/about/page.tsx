import Link from 'next/link';

export default function AboutPage() {
  return (
    <main className="bg-white">
      <section className="border-b border-gray-200">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">About Torus Coffee Company</h1>
          <p className="mt-4 text-lg text-gray-600">
            Freeze-dried snacks and coffee crafted in Iowa City.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-12">
        <div className="space-y-6 text-gray-700">
          <p>
            Torus Coffee Company is a small business focused on high-quality freeze-dried snacks
            and coffee. We believe in simple ingredients, bold flavor, and making something worth
            sharing.
          </p>
          <p>
            Based in Iowa City, we sell at local markets, online, and through wholesale partners.
            Every order is packed by hand and shipped fast.
          </p>
          <p>
            Questions or wholesale interest? <Link href="/contact" className="text-gray-900 underline">Contact us</Link>.
          </p>
        </div>
      </section>
    </main>
  );
}
