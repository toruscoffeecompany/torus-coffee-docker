# Payment Processor Setup Guide — Torus Coffee Company

## Goal
Accept payments on the public website with **$0 upfront cost** using free-tier tools.

## Recommended Stack

### Primary: Square Payment Links
- **Cost:** Free to create links; 2.9% + 30¢ per transaction
- **Setup time:** 15 minutes
- **What you need:** Square account + bank account for payout
- **Why:** Already documented in Revenue_Stream_Plan.md; free card reader available

### Backup: Venmo Personal
- **Cost:** Free for personal; 1.9% + 10¢ for business (if upgraded)
- **Setup time:** 5 minutes
- **Why:** Already documented; good for in-person markets

### Future: Stripe
- **Cost:** Free to set up; 2.9% + 30¢ per transaction
- **Why:** Best developer experience, but requires business verification

## Implementation

### 1. Square Payment Links (Recommended)
1. Go to squareup.com → Sign up for free account
2. Complete business profile (use existing EIN)
3. Link US Bank account for payouts
4. Create payment links for each product:
   - Solar Strawberries — $12.99
   - Sour Aurora Bites — $10.99
   - etc.
5. Add links to website product pages

### 2. Website Integration
Update `06_Website/website/app/products/page.tsx`:
```tsx
<button 
  onClick={() => window.open('https://square.link/u/...', '_blank')}
  className="rounded-lg bg-gray-900 px-5 py-3 text-white"
>
  Buy Now — $12.99
</button>
```

### 3. Formspree for Contact Form (Free Tier)
1. Go to formspree.io → Sign up
2. Create new form
3. Copy endpoint URL
4. Add to `.env`:
   ```
   CONTACT_FORMSPREE_URL=https://formspree.io/f/your-form-id
   ```
5. Contact API route already wired to use Formspree

## Free-Tier Alternatives

| Tool | Cost | Use Case |
|------|------|----------|
| Square Payment Links | Free + 2.9%/txn | Website checkout |
| Venmo Personal | Free | In-person markets |
| Formspree | Free (50 submissions/mo) | Contact form backend |
| Zapier Webhooks | Free (100 tasks/mo) | Form → Gmail → Obsidian |
| HubSpot CRM | Free (1,000 contacts) | Customer tracking |

## What We Can Build Now (No Bank API Needed)

1. **Square Payment Links** — create links, add to website
2. **Formspree contact form** — already coded, just needs endpoint
3. **Zapier webhook** — already coded, just needs webhook URL
4. **Venmo QR codes** — generate for in-person markets
5. **Order tracking** — order_manager.py already built

## What Needs Your Input

1. **Square account** — do you want to use existing account or create new?
2. **US Bank linking** — can you add US Bank to Square for payouts?
3. **Venmo business** — upgrade to business account or keep personal?
4. **Product pricing** — finalize prices for all 10 SKUs

## Next Steps

1. [ ] Create Square account / verify existing
2. [ ] Link US Bank account to Square
3. [ ] Create payment links for each product
4. [ ] Test end-to-end: website → Square → US Bank
5. [ ] Set up Formspree for contact form
6. [ ] Update website with payment links
