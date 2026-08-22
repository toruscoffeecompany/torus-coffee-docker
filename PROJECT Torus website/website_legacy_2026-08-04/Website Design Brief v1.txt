# Torus Coffee Company Website Design Brief

Last updated: 2026-05-29

## Project Goal
Build a real ecommerce platform for Torus Coffee Company, released in phases. The first public launch should be lean enough to get selling quickly, while the design and data model should support the larger long-term platform: customer accounts, product management, inventory tracking, blog publishing, shipping, analytics, and future Square API integration.

## Business Priorities
1. Sell products online nationwide in the United States.
2. Keep the site affordable to run while sales are still growing.
3. Make product, pricing, inventory, photo, and blog updates manageable by the business owner without editing code.
4. Build customer trust after a first year with limited sales.
5. Prepare for future wholesale/grocery expansion without making wholesale the main launch focus.

## Brand Direction
Business name: Torus Coffee Company

Core public message:
- Stay Curious. Stay Crunchy. Stay Cosmic.
- Freeze-dried candy, fruit, snacks, and cosmic kitchen experiments from Iowa.

Visual direction:
- Combine the existing logo/business card style with the current magical/cosmic site direction.
- Use midnight/navy space backgrounds, cream/light surfaces, gold highlights, purple and teal accents, and product color moments.
- Keep the experience playful and cosmic, but clear enough that shoppers can easily understand products, prices, shipping, and checkout.

Tone:
- Warm, Midwest, playful, slightly witchy/cosmic, clear, honest, and handmade.
- Avoid sounding corporate.
- Product pages should be fun, but the buying path must feel trustworthy and simple.

## Launch Products
The following products are ready to buy now:
- Star-Dusted Banana Crunch 1.15oz
- Apple Cinnamon Comets 1.15oz
- Aurora Berryalis 2.6oz
- Sour Aurora Bites 2.6oz
- Solar Strawberries 0.5oz
- Cosmic Bananas 1.55oz
- Aurora Bites 2.6oz
- Apple Zephyr Chips 1.15oz

Each product needs:
- Product name
- SKU
- Price
- Inventory count
- Product category
- Product description
- Product photos
- Weight
- Square payment/checkout link for the first launch phase
- Active/inactive status
- Optional low-stock threshold

## Ecommerce Strategy
Phase 1 should use Square checkout/payment links so the business can start selling quickly.

Long term, the platform should support deeper Square integration:
- Full checkout on site or embedded checkout flow
- Square order syncing
- Inventory subtraction after purchase
- Customer syncing
- Future catalog/order automation

Customer accounts should be optional, not required to buy. Guest checkout must remain available.

Orders still need shipping details. In the Square-link phase, Square checkout should collect the shipping address. If the site later owns checkout, the site must collect and validate shipping name, email, phone, address, city, state, ZIP, and shipping method.

## Shipping
- Ship to United States only.
- No international shipping at launch.
- Future shipping API integration may be needed for labels, rates, tracking, or carrier automation.
- The early version can use manual shipping rules if Square handles checkout.

## Inventory
Initial inventory tracking can be manual inside the site/admin system.

Long-term inventory goals:
- Add/subtract stock manually
- Low-stock warnings
- Product active/inactive controls
- Inventory adjustment history
- Automatic subtraction after paid orders once Square API integration is implemented
- Optional restock/addition workflow after production batches

## Admin Dashboard Requirements
The platform should eventually include a private admin dashboard with:
- Product list
- Add/edit/archive products
- Price editor
- Inventory editor
- Product photo upload/manager
- Category controls
- Product description editor
- Square checkout link field
- Blog editor
- Draft/published scheduling status
- Customer list
- Order/customer notes, where possible
- Error report viewer or links to error reports
- Backup/export tools

## Blog Requirements
The site should support three blogs/categories:
- The Orbit Report
- The Orbit Workshop
- The Orbit Kitchen

Blog editor needs:
- Draft and published status
- Title
- Slug/URL
- Category
- Author
- Featured image
- Body content
- Inline images
- Optional embedded videos
- SEO title/meta description
- Publish date
- Tags

Future video support should be planned, but the first version can support embedded video links or hosted video embeds before building native video hosting.

## Customer Accounts And Client Database
Customer accounts should be optional.

Needed long term:
- Email/password or magic-link login
- Customer profile
- Saved email/phone/address, if user opts in
- Order history, once orders are integrated
- Email signup consent
- Marketing consent tracking
- Customer export

Privacy and legal pages must clearly explain what customer data is collected and why.

## Social Media And Ads
The site should link to business social profiles.

Early phase:
- Public social links
- Share buttons for products and blog posts
- Product images sized for social sharing
- Analytics/pixels planned but not necessarily installed on day one

Later phases:
- Meta Pixel
- TikTok Pixel
- Pinterest tag
- Google Analytics
- Product catalog feeds for Meta/Pinterest, if useful
- Ad campaign workflow support

Directly publishing ads from the website should be treated as a later phase because ad APIs require platform permissions, business verification, ad accounts, and ongoing API maintenance.

## Error Reporting And Observability
The website needs a way for the owner/developer to understand errors.

Phase 1:
- User-friendly error messages on forms/admin actions
- Basic server/client logs from the hosting platform
- Clear admin-facing states when saving products/blog posts fails

Platform phase:
- Error reporting service integration such as Sentry or similar
- Frontend error capture
- Backend/API error capture
- Source maps for readable stack traces
- Contact/order/product action context where safe and privacy-conscious
- Admin error log page or direct links to the external error dashboard
- Manual support report form for customers to describe an issue

## Legal And Policy Pages
Needed before launch:
- Privacy Policy
- Terms and Conditions
- Refund and Returns Policy
- Shipping Policy
- Accessibility Statement

Existing Google Docs appear to exist for these, but local .gdoc files were not readable directly from the file system. Exported text/docx/pdf copies may be needed before implementation.

## Suggested Site Map
Public:
- Home
- Shop
- Product Detail
- Blog Home
- Blog Category: The Orbit Report
- Blog Category: The Orbit Workshop
- Blog Category: The Orbit Kitchen
- Blog Post Detail
- About
- Events / Find Us
- Contact
- Wholesale / Retail Partners, later or soft-launched
- Privacy Policy
- Terms and Conditions
- Refund and Returns Policy
- Shipping Policy
- Accessibility Statement

Private/Admin:
- Login
- Dashboard
- Products
- Add/Edit Product
- Inventory
- Blog Posts
- Add/Edit Blog Post
- Customers
- Orders, future
- Settings
- Error Reports / Diagnostics
- Exports / Backups

## Open Decisions
1. Confirm The Orbit Kitchen as the recipe blog name.
2. Decide the exact launch hosting/backend stack.
3. Choose whether Phase 1 admin is a real dashboard or a simpler structured-data editor.
4. Choose customer account provider/auth approach.
5. Decide shipping/rate strategy for the Square-link launch phase.
6. Confirm public email, phone, and social handles.
7. Locate/export final legal policy text.
8. Locate final product photos for all launch products.
9. Decide whether wholesale is visible at launch as a simple inquiry page or held for a later version.
10. Decide launch analytics/pixel level.
