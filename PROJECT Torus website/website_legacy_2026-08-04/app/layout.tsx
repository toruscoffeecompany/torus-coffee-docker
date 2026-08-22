import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Torus Coffee Company',
  description: 'Freeze-dried snacks and coffee from Iowa City',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <Link href="/" className="text-xl font-bold text-gray-900">
              Torus Coffee Company
            </Link>
            <nav className="flex gap-6 text-sm text-gray-700">
              <Link href="/products" className="hover:text-gray-900">Products</Link>
              <Link href="/about" className="hover:text-gray-900">About</Link>
              <Link href="/contact" className="hover:text-gray-900">Contact</Link>
            </nav>
          </div>
        </header>
        {children}
        <footer className="border-t border-gray-200 bg-white">
          <div className="mx-auto max-w-6xl px-6 py-8 text-sm text-gray-600">
            <div className="flex flex-wrap gap-4">
              <Link href="/legal/privacy-policy" className="hover:text-gray-900">Privacy Policy</Link>
              <Link href="/legal/terms" className="hover:text-gray-900">Terms</Link>
              <Link href="/legal/accessibility-statement" className="hover:text-gray-900">Accessibility</Link>
            </div>
            <p className="mt-4"> Torus Coffee Company. Freeze-dried in Iowa City.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
