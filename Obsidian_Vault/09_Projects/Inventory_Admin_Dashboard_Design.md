# Torus Coffee Company — Inventory Admin Dashboard Design
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** Draft

## Goal
Provide Pink with a free-tier/local-first admin view for inventory thresholds, sync status, and low-stock alerts.

## Schema Extensions
- `sku`: existing
- `qty`: existing
- `low_stock_threshold`: integer, default = 2
- `reorder_point`: integer, default = 5
- `last_synced_at`: ISO timestamp
- `sync_source`: enum: `inventory_master`, `website_generator`, `manual`

## Admin API Endpoints
- `GET /api/admin/inventory/low-stock`
  - Returns products where `qty <= low_stock_threshold`
  - Admin auth required
- `POST /api/admin/inventory/adjust`
  - Input: `sku`, `delta`, `reason`
  - Writes to `inventory_adjustments`
- `GET /api/admin/inventory/adjustments`
  - Returns audit log for inventory changes

## Frontend Components
- Admin inventory table with sort/filter by SKU/qty/threshold
- Low-stock highlight row with reorder link
- Sync status chip: `Synced`, `Stale`, `Error`
- Adjustment modal with reason field

## Access Control
- Use existing FastAPI admin key via `app.state.admin_api_key`
- Admin pages behind `/admin` route prefix
- No public exposure

## Integration
- Reads from `inventory_master.json`
- Writes adjustments to SQLite
- Triggered after `inventory_sync.py` runs
- Alerted via `alerts.json`

## Free-Tier Hosting
- Admin dashboard remains local-network only
- Vercel public site does not expose `/admin`
