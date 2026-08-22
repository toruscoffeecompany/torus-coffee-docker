# GitHub Workflow
_Last updated: 2026-07-22_

## Branching
- `main` — production-ready, deployable only by PR review.
- `develop` — integration branch for finished work.
- `feature/*` — single-purpose branches; name after the card or file scope.
- `hotfix/*` — urgent production fixes off `main`; merge back into `main` and `develop`.

## PR Rules
- Base: `develop` for feature branches; `main` for hotfixes/releases.
- Title: imperative mood. Example: `feat: add product list page`.
- Require at least one comment review on `main` merges.
- Keep PRs small. If review is slow, split.
- Link issue in PR body with `Fixes #<number>` or `Closes #<number>`.

## Labels to Keep
- `in-progress`
- `ready`
- `review`
- `blocked`
- `area:website`, `area:ops`, `area:finance`, `area:legal`, `area:growth`

## Commit Style
- Use conventional prefixes where useful: `feat`, `fix`, `docs`, `chore`.
- Owner-focused only: no commit secrets, env files, or vendor assets.

## Release Convention
- Versioning is minimal until first customer release.
- Git tags use `vYYYY.MM.DD` or `v0.X` once external-facing.
- Release notes summarize changed behavior, linked PRs/issues, and any manual deploy notes.
- Deploy target: Vercel or chosen platform, after owner approval.

## CODEOWNERS Hint
- All files: owner approval required for PRs to `main`.
- Website routes and deploy config: web contributor suggested review.
- Financial/workflow docs: ops contributor suggested review.
- Create `.github/CODEOWNERS` when the repo is initialized.

## CI Hint
- Keep pipeline simple.
- Actions to run on push/PR: install deps, lint, build.
- Do not run secrets-heavy jobs on public forks.
- Use caching for installs to keep free-tier minutes low.
