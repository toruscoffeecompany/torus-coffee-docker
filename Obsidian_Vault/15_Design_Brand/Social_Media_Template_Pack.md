# Social Media Template Pack — Torus Coffee Company

**Status:** Template specs ready  
**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Brand Source:** `08_Design_Brand/Brand_Style_Guide.md`

## Templates Overview

This pack contains specs for 24 social media templates:
- 8 template types
- 3 sizes each
- All using Torus Coffee Company brand colors and fonts

## Brand Colors

- **Deep Space Blue:** `#0a0e27` (backgrounds)
- **Cosmic Purple:** `#2d1b69` (accents)
- **Orange Solar:** `#ff6b35` (highlights, CTAs)
- **Cyan Orbit:** `#00d4ff` (borders, icons)
- **White:** `#ffffff` (text)

## Brand Fonts

- **Headlines:** Orbitron (sci-fi feel)
- **Body:** Inter (clean, readable)

## Logo Placement

- Position: Top center or bottom center
- Margin: Minimum 10% on all sides
- Never stretch or distort
- Minimum size: 100px wide

## Template Types

### 1. Product Announcement
**Use:** New product launches, restocks  
**Sizes:**
- Instagram Post: 1080x1080
- Facebook Post: 1200x630
- Pinterest Pin: 1000x1500

**Layout:**
- Top: Logo (centered)
- Center: Product image (80% of canvas)
- Bottom: Product name + tagline
- CTA: "Shop Now" button in orange

**Example:**
```
┌─────────────────────────┐
│       [LOGO]            │
│                         │
│    [PRODUCT IMAGE]      │
│                         │
│  Product Name           │
│  "Cosmic coffee,        │
│   freeze-dried magic"   │
│  [SHOP NOW]             │
└─────────────────────────┘
```

### 2. Market Event
**Use:** Farmers markets, craft shows, festivals  
**Sizes:**
- Instagram Post: 1080x1080
- Instagram Story: 1080x1920
- Facebook Event: 1920x1005

**Layout:**
- Top: Logo
- Center: Event details (date, time, location)
- Bottom: QR code to website
- CTA: "Come visit us!"

**Example:**
```
┌─────────────────────────┐
│       [LOGO]            │
│                         │
│   Iowa City Farmers     │
│        Market           │
│                         │
│   Saturday, Aug 2       │
│   8am - 12pm            │
│   Downtown Plaza        │
│                         │
│   [QR CODE]             │
│   Scan for details!     │
└─────────────────────────┘
```

### 3. Customer Testimonial
**Use:** Reviews, feedback, social proof  
**Sizes:**
- Instagram Post: 1080x1080
- Twitter Post: 1200x675
- Facebook Post: 1200x630

**Layout:**
- Top: Quote marks (large, cyan)
- Center: Customer quote
- Bottom: Customer name + product photo

**Example:**
```
┌─────────────────────────┐
│                         │
│    "These freeze-dried  │
│     candies are out of  │
│     this world!"        │
│                         │
│     - Sarah J.          │
│     [Product Photo]     │
│                         │
└─────────────────────────┘
```

### 4. Behind the Scenes
**Use:** Production process, team photos, facility  
**Sizes:**
- Instagram Post: 1080x1080
- Instagram Story: 1080x1920
- YouTube Thumbnail: 1280x720

**Layout:**
- Full-bleed image
- Overlay: Deep blue gradient at bottom
- Text: White, bottom center
- Logo: Top right

**Example:**
```
┌─────────────────────────┐
│ [LOGO]                  │
│                         │
│    [BTS IMAGE]          │
│                         │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ How we freeze-dry       │
│ your favorite candies   │
└─────────────────────────┘
```

### 5. Holiday/Special Occasion
**Use:** Halloween, Christmas, Valentine's, etc.  
**Sizes:**
- Instagram Post: 1080x1080
- Instagram Story: 1080x1920
- Pinterest Pin: 1000x1500

**Layout:**
- Themed background (seasonal colors)
- Center: Holiday product bundle
- Top: Logo
- Bottom: Promo text + CTA

**Example:**
```
┌─────────────────────────┐
│       [LOGO]            │
│                         │
│   [HALLOWEEN BUNDLE]    │
│                         │
│   25% OFF THIS WEEK     │
│   [SHOP NOW]            │
└─────────────────────────┘
```

### 6. Educational/How-To
**Use:** Blog posts, recipes, usage ideas  
**Sizes:**
- Instagram Post: 1080x1080
- Twitter Post: 1200x675
- Pinterest Pin: 1000x1500

**Layout:**
- Left: Step number (large, orange)
- Right: Step description + image
- Bottom: Link to blog

**Example:**
```
┌─────────────────────────┐
│       [LOGO]            │
│                         │
│  ① [IMAGE]              │
│  How to use freeze-     │
│  dried candy in your    │
│  favorite recipes       │
│                         │
│  Read more ->           │
└─────────────────────────┘
```

### 7. Wholesale/B2B
**Use:** Vendor outreach, bulk orders, partnerships  
**Sizes:**
- Instagram Post: 1080x1080
- LinkedIn Post: 1200x627
- Email Header: 600x200

**Layout:**
- Professional, clean
- Product grid (4 products)
- Text: "Become a vendor" + contact info
- Logo: Top center

**Example:**
```
┌─────────────────────────┐
│       [LOGO]            │
│                         │
│  [P1] [P2] [P3] [P4]   │
│                         │
│  Become a Vendor        │
│  Wholesale pricing      │
│  available now          │
│                         │
│  Contact: [email]       │
└─────────────────────────┘
```

### 8. Brand Awareness
**Use:** Company news, milestones, team introductions  
**Sizes:**
- Instagram Post: 1080x1080
- Facebook Post: 1200x630
- Twitter Post: 1200x675

**Layout:**
- Full brand colors
- Large text: Announcement
- Logo: Prominent
- Subtext: Details

**Example:**
```
┌─────────────────────────┐
│                         │
│       [LOGO]            │
│                         │
│   WE'RE AT THE          │
│   IOWA CITY FARMERS     │
│       MARKET!           │
│                         │
│   Come say hello this   │
│   Saturday at 8am       │
│                         │
└─────────────────────────┘
```

## File Naming Convention

```
[template_type]-[platform]-[size]-[version].[ext]

Examples:
- product-announcement-instagram-1080x1080-v1.png
- market-event-instagram-story-1080x1920-v1.png
- testimonial-twitter-1200x675-v1.png
```

## Sir Azure Generation Prompts

Each template should be generated with:
```
Social media template for Torus Coffee Company,
[template type],
[platform] size [dimensions],
brand colors: deep space blue #0a0e27,
cosmic purple #2d1b69, orange solar #ff6b35, cyan #00d4ff,
fonts: Orbitron + Inter,
logo placement: [position],
[additional details],
professional design, high resolution, PNG
```

## Tracking

- [ ] Create 24 template files (8 types x 3 sizes)
- [ ] Store in `08_Design_Brand/Social_Media_Templates/`
- [ ] Test on all platforms
- [ ] Get feedback from team
- [ ] Finalize templates
- [ ] Create usage guide

## Usage

- Use templates for all social media posts
- Maintain consistency across platforms
- Update templates quarterly
- Archive old templates to `08_Design_Brand/Archive/`
