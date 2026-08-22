# Netlify Deployment Guide

## Prerequisites
- Netlify account (free): https://app.netlify.com/signup
- Netlify CLI: `npm install -g netlify-cli`

## Deploy Steps

1. Login to Netlify:
   ```bash
   netlify login
   ```

2. Initialize site (first time only):
   ```bash
   cd D:/Work/Torus Coffee Company LLC/06_Website/Website
   netlify init
   ```
   - Choose "Create & configure a new site"
   - Select team
   - Site name: `torus-coffee-website` (or similar)
   - Build command: `npm run build`
   - Publish directory: `out`

3. Deploy:
   ```bash
   netlify deploy --prod
   ```

## Alternative: Git-based Deploy

1. Push this folder to a new GitHub repo `toruscoffeecompany/torus-website`
2. In Netlify: "New site from Git" → select repo
3. Build settings:
   - Build command: `npm run build`
   - Publish directory: `out`
4. Deploy

## Notes
- Free tier includes 100GB bandwidth/month
- Custom domain can be added later
- HTTPS is automatic
