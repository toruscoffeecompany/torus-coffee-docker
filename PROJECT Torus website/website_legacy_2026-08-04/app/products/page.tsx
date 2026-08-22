import Link from 'next/link';
import { Suspense } from 'react';

const PRODUCTS = [
  { name: 'Neapolitan Orbit Cream Crunch', price: 6.98, size: '2.0oz', sku: 'TCC-NOCC-200', desc: 'Freeze-Dried Neapolitan Ice Cream Sandwiches' },
  { name: 'Orbit Cream Crunch', price: 6.98, size: '2.0oz', sku: 'TCC-OCC-200', desc: 'Freeze-Dried Vanilla Ice Cream Sandwiches' },
  { name: 'Star-Dusted Banana Crunch', price: 5.98, size: '1.15oz', sku: 'TCC-SDB-115', desc: 'Freeze-Dried Bananas with Cinnamon Sugar' },
  { name: 'Apple Cinnamon Comets', price: 5.98, size: '1.15oz', sku: 'TCC-ACC-115', desc: 'Freeze-Dried Apple with Cinnamon Sugar' },
  { name: 'Aurora Berryalis', price: 4.98, size: '2.6oz', sku: 'TCC-ARB-26', desc: 'Freeze-Dried Wild Berry Skittles' },
  { name: 'Sour Aurora Bites', price: 4.98, size: '2.6oz', sku: 'TCC-SAB-26', desc: 'Freeze-Dried Sour Skittles' },
  { name: 'Solar Strawberries', price: 6.98, size: '0.5oz', sku: 'TCC-SS-05', desc: 'Freeze-Dried Strawberries' },
  { name: 'Cosmic Bananas', price: 5.98, size: '1.55oz', sku: 'TCC-CB-155', desc: 'Freeze-Dried Bananas' },
  { name: 'Aurora Bites', price: 4.98, size: '2.6oz', sku: 'TCC-AB-26', desc: 'Freeze-Dried Skittles' },
  { name: 'Apple Zephyr Chips', price: 5.98, size: '1.15oz', sku: 'TCC-AZC-115', desc: 'Freeze-Dried Apples' },
];

function ProductCard({ product }: { product: typeof PRODUCTS[0] }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
      <div className="aspect-square rounded-lg bg-gray-100 mb-4" />
      <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
      <p className="mt-1 text-sm text-gray-600">{product.desc}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-lg font-bold text-gray-900">${product.price.toFixed(2)}</span>
        <span className="text-xs text-gray-500">{product.size}</span>
      </div>
      <p className="mt-2 text-xs text-gray-400">SKU: {product.sku}</p>
    </div>
  );
}

export default function ProductsPage() {
  return (
    <main className="bg-white">
      <section className="border-b border-gray-200">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">Products</h1>
          <p className="mt-4 text-lg text-gray-600">
            Freeze-dried snacks crafted in Iowa City. Ready to ship.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <Suspense fallback={<div className="col-span-full text-center text-gray-500">Loading products...</div>}>
            {PRODUCTS.map((product) => (
              <ProductCard key={product.sku} product={product} />
            ))}
          </Suspense>
        </div>
      </section>
    </main>
  );
}
