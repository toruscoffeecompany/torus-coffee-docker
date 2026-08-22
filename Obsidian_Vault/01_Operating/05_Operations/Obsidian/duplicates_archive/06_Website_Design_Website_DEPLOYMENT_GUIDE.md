# Deploying Your Torus Coffee Company Website to Netlify

## What You Just Got
A beautiful, fully-functional website for Torus Coffee Company that includes:
- **Hero section** with your brand identity
- **Products showcase** with 6 product cards (customize these!)
- **About section** highlighting your story and Midwest community vibe
- **Contact form** for wholesale inquiries and customer messages
- **Responsive design** that looks great on phones, tablets, and computers
- **Witchy/space theme** with purple and gold colors

## Option 1: Deploy in 5 Minutes (Easiest!)

### Step 1: Create a Netlify Account
1. Go to **netlify.com**
2. Click "Sign up" (use email or GitHub)
3. Verify your email

### Step 2: Deploy Your Site
1. Download the `index.html` file from the outputs folder
2. Go back to Netlify dashboard
3. Look for the area that says "Drag and drop your site folder here" or "Create a new site"
4. **Drag your `index.html` file into the Netlify area**
5. Done! Netlify will generate a free URL like `mystatic-site.netlify.app`

### Step 3: Get Your Own Custom Domain (Optional but Recommended)
1. In Netlify, go to Domain settings
2. Click "Add domain"
3. Buy a domain name (Netlify uses Namecheap, or bring your own)
4. Popular options: `toruscoffeeco.com`, `toruscoffeecompany.com`

---

## Option 2: Deploy with GitHub (For Future Updates)

### Step 1: Create a GitHub Account
1. Go to **github.com**
2. Sign up with email
3. Verify your email

### Step 2: Create a New Repository
1. Click the **+** icon (top right) → "New repository"
2. Name it: `torus-coffee-website`
3. Choose "Public" (so Netlify can access it)
4. Click "Create repository"

### Step 3: Upload Your File
1. Click "uploading an existing file"
2. Drag and drop your `index.html` file
3. Commit the file with message: "Initial website commit"

### Step 4: Connect to Netlify
1. Go to **netlify.com**
2. Click "New site from Git"
3. Connect to GitHub
4. Select the `torus-coffee-website` repository
5. Click "Deploy site"
6. Netlify will assign a URL automatically!

---

## Customizing Your Website

### Change Product Information
Open `index.html` in a text editor and find this section:

```html
<div class="product-card">
    <div class="product-image">☕</div>
    <div class="product-info">
        <h3>Freeze-Dried Coffee Snacks</h3>
        <p>Unique coffee-inspired treats...</p>
    </div>
</div>
```

- Replace `☕` with any emoji representing your product
- Update the title and description
- Change `<span class="badge">Popular</span>` to `New` or `Sale` as needed

### Add Real Product Photos
Replace the emoji with actual images:

```html
<img src="path-to-your-image.jpg" style="width: 100%; height: 200px; object-fit: cover;">
```

Store images in the same folder as `index.html`, or upload to a free image hosting site like Imgur or Cloudinary.

### Update Contact Information
Find the contact section and update:
- Email: Change `hello@toruscoffee.com` to your actual email
- Phone: Add your phone number or keep as-is
- Social media links: Replace `#` with actual links to Instagram, Facebook, TikTok

### Change Colors
The main colors are:
- **Purple**: `#2d1b4e` (dark purple)
- **Gold**: `#ffd700` (yellow-gold)
- **Light**: `#f8f6ff` (off-white)

Search for these hex codes in the file and swap them for your preferences.

---

## Important Next Steps

### 1. Update the Email Form
The current form shows an alert. To actually receive emails, use a free service:
- **Formspree** (free): Go to formspree.io, create account, replace `<form>` with their code
- **Basin** (free): basin.io - similar setup
- **Netlify Forms** (free): Add `netlify` attribute to form tag

### 2. Set Up Social Media Links
Replace the `#` placeholders in the footer with real links:
```html
<a href="https://instagram.com/yourhandle" title="Instagram">
```

### 3. Add Google Analytics (Optional)
Track visitors at no cost:
1. Go to **google.com/analytics**
2. Create account for your website
3. Copy the tracking code
4. Paste it before `</body>` tag in index.html

### 4. Add Your Logo/Brand Assets
- Replace the 🪐 emoji in the header with a real logo image
- Create a witchy-themed favicon (the tiny icon in browser tab)

---

## Free Tools You'll Need

| Task | Tool | Cost |
|------|------|------|
| Hosting | Netlify | Free |
| Domain | Namecheap or Netlify | $10-15/year |
| Images | Imgur, Cloudinary | Free |
| Email Forms | Formspree, Basin | Free |
| Analytics | Google Analytics | Free |
| Text Editor | VS Code | Free |

---

## Tips for Grocery Store Success

Your website is now set up to attract wholesale buyers! Here's how to optimize:

1. **Add a "For Retailers" section** - Create a simple page about bulk ordering and margins
2. **Professional contact info** - Make sure email and phone are easy to find
3. **Clear product descriptions** - Include ingredients, shelf life, storage info
4. **Food safety certifications** - Display any certifications prominently
5. **Flea market locations & dates** - Keep this updated (grocery stores want to know you're established)

---

## Troubleshooting

**"My images aren't showing"**
- Make sure image files are in the same folder as index.html
- Use relative paths: `image.jpg` not `/image.jpg`

**"Form isn't working"**
- Netlify forms require the `netlify` attribute on the `<form>` tag
- Or use Formspree/Basin for email

**"Colors look weird on my phone"**
- This is normal! The site is responsive. Test in browser's mobile view.

**"I want to change fonts"**
- Search for `font-family` in the CSS section
- Replace with any Google Font name

---

## You're Ready! 🪐✨

Your website is live and ready to impress grocery store buyers and customers. Next steps:
1. Deploy to Netlify
2. Add real photos and contact info
3. Test on phone and desktop
4. Share the link on your social media
5. Use it in your pitch to grocery stores!

Need help? Netlify has great support, and the code is simple enough to tweak in any text editor.

**Saving food since Iowa City—you've got this! ❄️✨**
