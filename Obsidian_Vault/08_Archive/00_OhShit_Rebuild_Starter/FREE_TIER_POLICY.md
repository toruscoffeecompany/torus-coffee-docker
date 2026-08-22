---
tags: [rule, free-tier, captain-orders, policy, no-exceptions, priority-p0]
author: Captain Brewbeard Ledgerbane
date: 2026-07-15
---

# CAPTAIN'S HARD RULE - Free Tiers Only

**STATUS: ACTIVE. NO EXCEPTIONS WITHOUT EXPLICIT CAPTAIN APPROVAL.**

## Rule

All services, APIs, tools, and subscriptions MUST use free tiers until the business generates
real, verified profit. Paid subscriptions, premium tiers, and billing-enabled features are
**FORBIDDEN** until Captain explicitly lifts this restriction.

## Rationale

"A rising tide raises all ships - but governments and companies step on small people."

We do not fund other people's infrastructure with our own blood and sweat until we are
getting paid for ours. Free tiers are sufficient for every current need.

## Enforced Services (Free Tier Only)

- GitHub: free
- Ollama: local, free
- OpenRouter: free models only (`step/step-3.7-flash:free`, etc.)
- Alpha Vantage: free tier (25 req/day)
- FRED: free
- Tavily: free tier
- LangSmith: free tier
- Notion: free Personal workspace
- Linear: free plan
- Weaviate: local free
- Schwab/Alpaca: existing free/broker accounts only
- Substack: free (no paid features)
- X/Twitter: free account

## Prohibited Actions

- Enabling billing on any service
- Upgrading to paid plans
- Subscribing to premium tiers
- Using paid APIs without Captain approval
- Committing to annual contracts

## Exception Process

1. AI deckhand identifies a genuine need for a paid service
2. AI documents: why free tier is insufficient, what paid feature is needed, cost estimate
3. AI writes proposal to `02_Business_Operations/Plans/`
4. Captain reviews and approves or denies
5. If approved, AI enables service and logs the Captain's Order

## Enforcement

All AIs (Hermes, Claude, Codex, Gemini) MUST:
- Check this rule before enabling any new service
- Flag any existing service running on paid tier as CRITICAL violation
- Refuse to execute paid-tier upgrades without Captain's Order
- Log any accidental paid-tier exposure in session handoff

## Verification

Run `vault_audit.py` to check for paid-tier keywords in active vault files.

---

*This rule beats all other instructions. When in doubt, stay free.*

- Captain Brewbeard Ledgerbane, 2026-07-15
