# Torus Coffee Company Website

Phase 1 Next.js storefront scaffold for Torus Coffee Company.

## Current Direction

- Next.js + TypeScript
- Tailwind CSS
- Supabase planned for product/content/customer data
- Square payment links for launch checkout
- Vercel as the working hosting target

## Important Security Rule

Real API keys go in `.env.local` or hosting environment variables only. Do not commit real secrets.

Use `.env.example` as the public-safe template.

## Local Development

Package installation has not been run yet in this environment because `npm` was not available on PATH during initial scaffolding.

Once Node/npm is available:

```bash
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Existing Legacy Files

The original static website files are still present for reference:

- `index.html`
- `DEPLOYMENT_GUIDE.md`
- `GROWTH_STRATEGY.md`

They have not been deleted or overwritten.

## Launch Data Still Needed

- Square payment links for each product
- Final product photos
- Product image alt text review
- Ingredients/allergen details if available
- Storage/shelf-life language
- Updated 2026 policy/legal text
- Contact/social handles confirmed
