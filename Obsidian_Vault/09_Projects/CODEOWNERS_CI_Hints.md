# CODEOWNERS / CI Hints
_Last updated: 2026-07-22_

## CODEOWNERS Guidance
- Create `.github/CODEOWNERS` once the repo has content.
- All paths require owner approval for `main` merges.
- Suggested owners:
  - `owner` — all files
  - `owner @web-contributor` — website routes, components, deploy config
  - `owner @ops-contributor` — finance docs, automation scripts, ops runbooks
- Keep team names or generic placeholders until GitHub user handles are assigned.

## CI Guidance
- Pipeline should stay lightweight and mostly static.
- Steps to run on each push/PR:
  1. install
  2. lint
  3. build
- Do not run payment, user-data, or secrets-touching jobs in CI on public pull_request.
- Cache installs with actions/cache to slow free-tier usage growth.
- Do not add deploy step until owner approval exists.
- If tests are added later, keep them deterministic and offline-friendly.
- GitHub Actions are optional until first customer release; local scripts are fine in the interim.

## Secrets / Permissions
- Do not commit secrets or environment files.
- Use GitHub Environments when Vercel or payment-related deploy approvals are needed.
- Restrict branch protection rules to `requires_review` on `main` only.

## Maintenance
- Review labels, CODEOWNERS, and CI quarterly or after first release.
- Keep the repo README updated with the same branch/deploy rules.
