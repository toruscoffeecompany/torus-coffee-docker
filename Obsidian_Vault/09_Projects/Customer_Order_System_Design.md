# Torus Coffee Company — Customer/Order System Design
**Date:** 2026-08-04
**Owner:** Miss Pink
**Status:** Draft

## Goal
Define a simple, free-tier customer and order system backed by SQLite.

## Customer Schema
- `id`: integer PK
- `name`: text
- `email`: text unique
- `phone`: text optional
- `address`: text optional
- `source`: enum: `contact_form`, `wholesale`, `manual`
- `created_at`: ISO timestamp

## Order Schema
- `id`: integer PK or human-readable `TCC-YYYYMMDD-NNN`
- `customer_id`: FK to customers
- `status`: enum: `new`, `processing`, `shipped`, `completed`, `canceled`
- `total`: numeric
- `notes`: text optional
- `created_at`: ISO timestamp

## Order Item Schema
- `id`: integer PK
- `order_id`: FK to orders
- `sku`: text
- `name`: text
- `qty`: integer
- `unit_price`: numeric
- `line_total`: numeric

## State Transitions
- `new` -> `processing` -> `shipped` -> `completed`
- Allowed cancel from `new` or `processing`

## Admin Tools
- `GET /api/admin/orders?status=new`
- `POST /api/admin/orders/{id}/status`
- `GET /api/admin/customers`
- Admin auth required

## Integration
- Contact inquiries can create customer records
- Future Square/webhook can create orders
- Customer orders visible in local admin only

## Free-Tier Constraints
- No paid CRM until revenue
- Local admin UI only; public site shows no customer data
