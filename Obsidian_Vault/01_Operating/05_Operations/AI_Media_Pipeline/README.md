# AI Media Pipeline — Sir Azure Integration

**Status:** Ready for Sir Azure setup  
**Date:** 2026-08-03  
**Owner:** Miss Pink  
**Purpose:** Automate AI art generation for all Torus Coffee Company assets

## Pipeline Overview

```
[Miss Pink Brief] -> [Trello Card] -> [Sir Azure/STEALTHATTACK] -> [Generated Assets] -> [Vault/Website]
```

## Asset Requests

### 1. Product Images
**Priority:** P1  
**Quantity:** 10 products x 6 images each = 60 images  
**Specs:**
- Hero: 1920x1080, 72 DPI
- Thumb: 600x600, 72 DPI
- Social: 1080x1080, 72 DPI
- Story: 1080x1920, 72 DPI
- Print: 3000x3000, 300 DPI
- Lifestyle: 1920x1080, 72 DPI

**Brand:**
- Deep space blue (#0a0e27)
- Cosmic purple (#2d1b69)
- Orange solar (#ff6b35)
- Cyan orbit (#00d4ff)
- Font: Orbitron (headlines), Inter (body)

**Prompt template:**
```
Product photography of [PRODUCT NAME], [DESCRIPTION], 
on [BACKGROUND], professional lighting, 
Torus Coffee Company brand colors [COLORS], 
cosmic space theme, freeze-dried candy texture, 
high detail, commercial photography style
```

### 2. Social Media Templates
**Priority:** P1  
**Quantity:** 8 templates x 3 sizes = 24 templates  
**Sizes:**
- Instagram Post: 1080x1080
- Instagram Story: 1080x1920
- Facebook Post: 1200x630
- Pinterest Pin: 1000x1500
- Twitter Post: 1200x675
- YouTube Thumb: 1280x720
- Email Header: 600x200
- Vendor Print: 3000x3000

**Brand:**
- All templates use brand colors
- Logo placement: top center or bottom center
- Minimum 10% margin on all sides
- Fonts: Orbitron + Inter

### 3. Vendor Booth Backdrop
**Priority:** P1  
**Size:** 10x10 feet (3000x3000px, 300 DPI)  
**Format:** PNG with transparency, PDF for print  
**Content:**
- Torus Coffee Company logo
- Tagline: "Cosmic coffee, freeze-dried magic"
- Product showcase
- QR code to website
- Contact info

### 4. Email Signatures
**Priority:** P2  
**Quantity:** 2 (Miss Pink + Sara Jane)  
**Sizes:**
- Banner: 600x150px
- Product badge: 200x200px
- Social icons: 40x40px each

### 5. Blog Images
**Priority:** P2  
**Quantity:** 12 images (1 per campaign)  
**Sizes:**
- Featured: 1200x630px
- Inline: 800x400px
- Thumbnail: 300x300px

### 6. Website Graphics
**Priority:** P2  
**Quantity:** 5-10 graphics  
**Sizes:**
- Hero banners: 1920x1080
- Product category images: 800x800
- Background patterns: 1920x1080 (seamless)

### 7. Animated Content
**Priority:** P3  
**Quantity:** 3-5 videos  
**Length:** 15-60 seconds each  
**Formats:** MP4, GIF
- Product showcase videos
- Behind-the-scenes
- Social media reels

## Automation Scripts

### 1. Asset Request Generator
**Location:** `scripts/generate_asset_request.py`  
**Function:** Creates Trello card with full brief for Sir Azure  
**Trigger:** Manual or scheduled

### 2. Asset Validator
**Location:** `scripts/validate_asset.py`  
**Function:** Checks generated assets against brand specs  
**Trigger:** Post-generation

### 3. Asset Organizer
**Location:** `scripts/organize_assets.py`  
**Function:** Moves completed assets to correct vault folders  
**Trigger:** Post-validation

### 4. Pipeline Scheduler
**Location:** `scripts/pipeline_scheduler.py`  
**Function:** Runs asset requests on schedule  
**Trigger:** Windows Task Scheduler

## Trello Integration

- [x] Trello board: Torus_Ops
- [x] Trello API configured
- [x] Asset request cards created
- [ ] Sir Azure to watch board for new requests
- [ ] Sir Azure to move cards to "In Progress" when started
- [ ] Sir Azure to move cards to "Review" when complete

## File Naming Convention

```
[PRODUCT]-[ASSET_TYPE]-[SIZE]-[VERSION].[ext]

Examples:
- aurora-bites-hero-1920x1080-v1.png
- social-template-instagram-1080x1080-v1.png
- vendor-backdrop-3000x3000-v1.png
```

## Storage

- **Source:** `08_Design_Brand/` (templates, guides)
- **Generated:** `08_Design_Brand/Generated/` (AI outputs)
- **Product:** `04_Products/Product_Photos/` (final product photos)
- **Social:** `06_Growth_Marketing/Social_Media/` (social graphics)
- **Export:** `08_Design_Brand/Export/` (ready-to-use files)

## Quality Control

- [ ] All assets match brand colors
- [ ] All assets use correct fonts
- [ ] Logo placement is correct
- [ ] No watermarks or artifacts
- [ ] Correct file format and size
- [ ] File naming follows convention

## Next Steps

1. [ ] Sir Azure to confirm STEALTHATTACK setup
2. [ ] Sir Azure to test AI art generation
3. [ ] Create asset request forms
4. [ ] Test pipeline with 1 product image
5. [ ] Scale to all products
