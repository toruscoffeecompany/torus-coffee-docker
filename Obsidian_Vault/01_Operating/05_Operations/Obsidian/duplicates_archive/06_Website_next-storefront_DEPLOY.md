# Torus Coffee Company – Website Deployment

## GitHub setup
1. Create a GitHub repo, e.g. `torus-coffee-website`
2. Add remote:

```bash
git remote add origin git@github.com:<USERNAME>/torus-coffee-website.git
git branch -M main
git push -u origin main
```

## Free hosting options

### GitHub Pages
- Recommended: build locally and deploy `out/` via GitHub Pages
- Use `next export` + static assets; less ideal for dynamic features

### Vercel
- Connect GitHub repo to Vercel
- Auto-deploys `main`
- Free tier sufficient for starter site

### Cloudflare Pages
- Connect GitHub repo
- Build command: `npm run build`
- Output: `.next` or custom if using static export

### Self-hosted
- Dockerfile/workflow provided if desired
- Not required for launch; use later if needed

## Environment
- Copy `.env.example` to `.env.local`
- Fill real values only in `.env.local`
- Never commit secrets

## First deploy checklist
- [ ] Final product photos in `public/images/products/`
- [ ] Square payment links in `data/products.ts`
- [ ] Legal pages reviewed
- [ ] Social handles confirmed
- [ ] Domain/email configured if desired later
