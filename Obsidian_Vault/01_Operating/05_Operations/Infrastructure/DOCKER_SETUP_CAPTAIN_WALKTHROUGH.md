# PINKCADY Docker + Cross-Host Setup — Captain Walkthrough
Date: 2026-08-06T01:25:00Z

## What I need from you, Captain
You only need to do **3 things** in this exact order. Everything else I do myself.

---

## Step 1 — Create Docker Hub account `toruscoffeecompany`
1. Open browser → https://hub.docker.com/signup
2. Username: `toruscoffeecompany`
3. Use your real email (free tier is fine)
4. Verify email
5. Log in

## Step 2 — Create Docker Hub Access Token (NOT your password)
1. Go to https://hub.docker.com/settings/security
2. Click **New Access Token**
3. Name: `torus-ops-push`
4. Permissions: **Read & Write**
5. Copy the token — it starts with `dckr_pat_...`
6. **Send it to me securely** — do NOT paste it in chat. Email it to yourself or put it in your local encrypted vault and tell me the path.

## Step 3 — Give me the token
Once you have `dckr_pat_...`, tell me where it lives. I will read it from there and never ask again.

---

## What I do after you finish Step 1–3
- Tag all `torus-*` and `void-*` images from SQUIDSTATION with `toruscoffeecompany/*`
- Push them to Docker Hub
- Configure PINKCADY ↔ SQUIDSTATION Docker networking via Tailscale
- Automate pulls so load distributes across rigs
- Send Sir Green + Sir Azure the exact connection strings

---

## If Docker Hub username `toruscoffeecompany` is taken
- Pick an alternate: `toruscoffeecohub`, `torus-coffee-docker`, `toruscoffee`
- Tell me the final username so I can update everything

---

## Captain summary
| Step | You do | I do |
|------|--------|------|
| 1 | Create Docker Hub account `toruscoffeecompany` | — |
| 2 | Create access token `dckr_pat_...` with Read & Write | — |
| 3 | Tell me the token path | Read it, start pushing |
| 4 | — | Tag, push, network, automate |
