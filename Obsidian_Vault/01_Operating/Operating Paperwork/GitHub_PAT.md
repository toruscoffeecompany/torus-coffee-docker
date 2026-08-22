# Torus Coffee Company — GitHub PAT Vault Secret

## Status: ✅ CONFIGURED
- Tokens stored in: `10_Skills_Library/05_Operations/secrets.local.json`
- Miss Pink GitHub token: ✅ Active (used for commits/pushes to Torus_Ops)
- Sir Azure GitHub token: ✅ Active (VOIDPirateTrade collaborator, push access)
- Sir Green GitHub token: ✅ Active (VOIDPirateTrade collaborator, push access)
- All tokens scoped to: `repo`, `workflow`, `read:org`, `write:packages`
- Secrets file is in `.gitignore` — never committed to repo

## Usage
```python
import json
secrets = json.load(open(Automation_DIR / "secrets.local.json"))
token = secrets["miss_pink_github_token"]  # or sir_azure/sir_green variants
```

## Rotation Schedule
- Tokens reviewed monthly
- Last rotated: 2026-08-06
- Next rotation due: 2026-09-06

## Security Notes
- `secrets.local.json` is listed in `.gitignore` as `secrets.local.json`
- Tokens are never logged or printed in output
- If PAT is expired/revoked, regenerate at: https://github.com/settings/tokens
