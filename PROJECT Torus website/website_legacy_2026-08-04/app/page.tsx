import Link from 'next/link';

export default function HomePage() {
  return (
    <main>
      <section className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">
            Torus Coffee Company
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            Freeze-dried snacks and coffee crafted in Iowa City.
          </p>
          <div className="mt-8 flex gap-4">
            <Link
              href="/products"
              className="rounded-lg bg-gray-900 px-5 py-3 text-white hover:bg-gray-800"
            >
              Shop products
            </Link>
            <Link
              href="/about"
              className="rounded-lg border border-gray-300 px-5 py-3 text-gray-900 hover:bg-gray-50"
            >
              About us
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
