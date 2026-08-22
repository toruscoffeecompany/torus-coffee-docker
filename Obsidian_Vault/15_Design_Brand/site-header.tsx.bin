import Link from "next/link";

const navItems = [
  { href: "/shop", label: "Shop" },
  { href: "/blog", label: "Blog" },
  { href: "/about", label: "About" },
  { href: "/find-us", label: "Find Us" },
  { href: "/contact", label: "Contact" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-midnight/95 text-cream backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4" aria-label="Main navigation">
        <Link href="/" className="flex items-center gap-3 font-display text-xl font-bold tracking-normal">
          <span className="grid h-10 w-10 place-items-center rounded-full border border-stardust/50 bg-cream text-midnight">T</span>
          <span>Torus Coffee Company</span>
        </Link>
        <div className="hidden items-center gap-7 md:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="text-sm font-semibold text-cream/85 transition hover:text-stardust">
              {item.label}
            </Link>
          ))}
          <Link href="/shop" className="rounded-full bg-stardust px-5 py-2 text-sm font-bold text-midnight transition hover:bg-cream">
            Shop Snacks
          </Link>
        </div>
      </nav>
    </header>
  );
}
