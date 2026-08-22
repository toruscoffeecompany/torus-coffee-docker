# Torus Coffee Company — SEO/Social Auto-Posting Design
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** Draft

## Goal
Design a free-tier SEO/social auto-posting system for local content generation and manual review.

## Free-Tier Toolchain
- Content generation: local scripts + Obsidian vault notes
- Scheduling: Task Scheduler + local queue file
- Posting: manual publish step until social APIs unlocked
- SEO metadata: generated into Next.js static pages

## Content Calendar Schema
- `post_id`: text
- `platform`: enum: `x`, `facebook`, `pinterest`, `substack`, `youtube`
- `title`: text
- `body`: text
- `media_paths`: json array
- `scheduled_at`: ISO timestamp
- `status`: enum: `draft`, `ready`, `published`, `failed`
- `tags`: json array

## Post Templates
- Product launch template
- Lore/cosmos snippet template
- Behind-the-scenes template
- Event/popup template

## Platform Routing Rules
- `x`: short text + 1 image
- `facebook`: longer text + link
- `pinterest`: image-first + link
- `substack`: long-form markdown
- `youtube`: title/description + link

## Approval Workflow
1. Generate draft from template + vault notes
2. Write to `02_Business_Operations/Content_Queue/`
3. Human review required before publish
4. Mark as `ready` or return to `draft`

## SEO Metadata
- Generate per-product meta titles/descriptions
- Generate sitemap entries
- Store in `06_Website/next-storefront/data/seo/`

## Automation
- `scripts/social_content_generator.py`
- `scripts/seo_metadata_generator.py`
- Task Scheduler job for weekly content batch

## Not Included Until Approved
- Direct API auto-posting
- Paid scheduling tools
