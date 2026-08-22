# Website Deployment Guide — Torus Coffee Company

**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Status:** Guide ready — Netlify recommended  
**Recommendation:** Netlify (free tier)

## Recommendation

**Why Netlify:**
- Free tier allows commercial use
- 100GB bandwidth/month
- 300 build minutes/month
- Free SSL certificate
- Custom domain support
- Git-based auto-deploy
- Form handling without backend
- Serverless functions
- Best for Next.js after Vercel
- No per-user pricing

**Alternatives considered:**
- Vercel: Best for Next.js, but free tier commercial use prohibited by some interpretations
- GitHub Pages: Free, but limited to 100GB bandwidth, no SPA routing, GitHub-only
- Cloudflare Pages: Unlimited bandwidth, but Workers runtime is not Node.js
- Render: Free static hosting, but very basic features

**Decision:** Netlify for free commercial hosting with best developer experience. Can migrate to Vercel later when revenue justifies $20/month.

## Setup Steps

### 1. Prepare Repository
```bash
cd D:/Work/Torus Coffee Company LLC/06_Website/next-storefront

# Ensure build works
npm run build

# Create .gitignore if missing
echo "node_modules" >> .gitignore
echo ".next" >> .gitignore
echo "out" >> .gitignore
```

### 2. Push to GitHub
```bash
# Create new repo on GitHub: toruscoffeecompany/torus-website
# Or use existing toruscoffeecompany/Torus_website_rebuild

git remote set-url origin https://github.com/toruscoffeecompany/Torus_website_rebuild.git
git push -u origin main
```

### 3. Deploy to Netlify
1. Go to https://app.netlify.com
2. Click "New site from Git"
3. Connect GitHub account
4. Select repository: `Torus_website_rebuild`
5. Build settings:
   - Build command: `npm run build`
   - Publish directory: `.next`
6. Click "Deploy site"

### 4. Configure Domain
1. In Netlify, go to Domain settings
2. Click "Add custom domain"
3. Enter: toruscoffeecompany.com
4. Follow DNS instructions:
   - Add CNAME record: `www` → `toruscoffeecompany.netlify.app`
   - Add A records for apex domain
5. Wait for DNS propagation (5-30 minutes)

### 5. Configure SSL
1. In Netlify, go to Domain settings
2. Click "HTTPS"
3. Click "Verify DNS configuration"
4. Click "Provision certificate"
5. Wait for Let's Encrypt issuance

### 6. Environment Variables
In Netlify dashboard:
- Go to Site settings → Environment variables
- Add:
  - `NEXT_PUBLIC_SITE_URL`: https://toruscoffeecompany.com
  - `NEXT_PUBLIC_GA_ID`: G-XXXXXXXXXX (after GA4 setup)

### 7. Test Deployment
- Visit https://toruscoffeecompany.netlify.app
- Test all pages:
  - Homepage
  - Shop
  - Product pages
  - About
  - Contact
  - Legal pages
- Test on mobile
- Test checkout flow

## Free Tier Limits

- **Bandwidth:** 100GB/month
- **Build minutes:** 300/month
- **Sites:** Unlimited
- **SSL:** Free
- **Forms:** 100 submissions/month
- **Functions:** 125,000 invocations/month

## Costs at Scale

- **Pro:** $19/month per user
- **Bandwidth overage:** $55/100GB
- **Extra build minutes:** $8/500 minutes

## Migration Path

When ready to upgrade:
1. Vercel: Best Next.js support, $20/month
2. Self-hosted: Docker on SQUIDSTATION, full control
3. Cloudflare Pages: Unlimited bandwidth, $5/month

## Next Steps

1. Push website to GitHub
2. Connect Netlify to GitHub
3. Deploy first version
4. Configure custom domain
5. Setup SSL
6. Test all functionality
7. Add payment links
8. Launch!

## Files

- `Website_Deployment_Guide.md` — this file
- `Square_Payment_Links_Setup.md` — payment setup
- `Google_Analytics_Setup_Guide.md` — analytics setup
