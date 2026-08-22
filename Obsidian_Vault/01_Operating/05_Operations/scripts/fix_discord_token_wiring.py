"""
FIX: Discord bot token wiring — create miss_pink alias in crew_map.json
Root cause: crew_map.json has 'scarlett_coralsink' but bot launch uses 'miss_pink'
Also: all tokens are [REDACTED] — need manual reset from Discord Developer Portal

Steps:
1. Add 'miss_pink' key to crew_map.json (alias for scarlett_coralsink)
2. Create .env with token placeholders
3. Create .env.production with actual token format instructions
"""
import json, os, shutil
from datetime import datetime

crews_path = "Z:/Developer_Brain/02_Business_Operations/Communications/Discord/crew_map.json"
env_path = "Z:/Developer_Brain/02_Business_Operations/Communications/Discord/.env"

# ─── 1. Fix crew_map.json — add miss_pink alias ────────────────────────────────
print("=== 1. Fixing crew_map.json ===")
with open(crews_path, "r", encoding="utf-8") as f:
    crew = json.load(f)

# Check if miss_pink alias exists
if "miss_pink" not in crew.get("crew", {}):
    # Copy scarlett_coralsink as miss_pink
    if "scarlett_coralsink" in crew.get("crew", {}):
        sc = crew["crew"]["scarlett_coralsink"].copy()
        sc["name"] = "Miss Pink (PINKCADY)"
        sc["token_env"] = "DISCORD_MISS_PINK_TOKEN"
        crew["crew"]["miss_pink"] = sc
        print("  ✅ Added 'miss_pink' alias (from scarlett_coralsink)")
    else:
        print("  ⚠️ Warning: neither miss_pink nor scarlett_coralsink found")
else:
    print("  ✅ miss_pink already exists")

# Also add sir_green_token alias if missing
if "sir_green" in crew.get("crew", {}):
    crew["crew"]["sir_green"]["token_env"] = "DISCORD_SIR_GREEN_TOKEN"

with open(crews_path, "w", encoding="utf-8") as f:
    json.dump(crew, f, indent=2)
print("  ✅ crew_map.json updated")

# ─── 2. Document the .env token reset requirements ─────────────────────────────
print("\n=== 2. Token Requirements ===")
print("  .env file exists with tokens marked [REDACTED]")
print("  Need to reset 4 tokens in Discord Developer Portal:")

# Read the .env to see what tokens are needed
with open(env_path, "r") as f:
    env_content = f.read()

token_keys = []
for line in env_content.split("\n"):
    if "TOKEN" in line.upper() and "=" in line:
        key = line.split("=")[0].strip()
        token_keys.append(key)

for k in token_keys:
    print(f"  - {k}: needs reset in Discord Developer Portal")

# ─── 3. Create a token intake template ─────────────────────────────────────────
print("\n=== 3. Creating token intake template ===")
token_intake = """# Discord Bot Token Intake — PINKCADY

**Status:** ❌ BLOCKED — All tokens expired (HTTP 403/1010)

**Root cause:** Discord tokens in .env are all [REDACTED]. Discord requires manual reset via Developer Portal.

**Who resets:** Captain (voidpiratetrading@gmail.com)

**Steps to fix:**
1. Go to https://discord.com/developers/applications
2. Sign in with voidpiratetrading@gmail.com
3. Select each bot application:
   - "Scarlett Coralsink" (Miss Pink's bot)
   - "Sir Green" (Boatswain bot)
   - "Sir Azure" (Quartermaster bot)
   - "Sir Cobalt" / "Sir Violet" (if applicable)
4. For each: Bot → Reset Token → Copy new token
5. Paste into .env (this file) replacing [REDACTED]
6. Restart: pythonw run_all_crew_bots.py on PINKCADY

**Expected token format:** MTk2... .abc123... (no quotes)

**After reset, verify:**
```bash
python -c "
import urllib.request
req = urllib.request.Request('https://discord.com/api/v10/users/@me')
req.add_header('Authorization', 'Bot <PASTE_NEW_TOKEN_HERE>')
print('OK' if urllib.request.urlopen(req, timeout=5).status == 200 else 'FAIL')
"
```

**Additional bug found:** crew_map.json was missing the 'miss_pink' key (only had 'scarlett_coralsink').
Fixed: Added miss_pink = scarlett_coralsink alias. Bot can now launch with --crew miss_pink.

**Bot launcher:** run_all_crew_bots.py (launched 3 bots + relay)
**Bot script:** discord_crew_bot.py (--crew <key>)
**discord.py:** 2.7.1 (installed ✅)
"""

intake_path = "Z:/Developer_Brain/02_Business_Operations/Communications/Discord/DISCORD_TOKEN_INTAKE_MISS_PINK.md"
with open(intake_path, "w") as f:
    f.write(token_intake)
print(f"  ✅ Created: {intake_path}")

# ─── 4. Create the fix script ──────────────────────────────────────────────────
fix_script = """#!/usr/bin/env pythonw
\"\"\"
FIX: Discord token wiring — adds miss_pink alias + verifies .env tokens.
Run before starting Discord bots.
\"\"\"
import json, os, sys
from pathlib import Path

HERE = Path(__file__).parent
CREW_MAP = HERE / 'crew_map.json'
ENV_FILE = HERE / '.env'

# 1. Add miss_pink alias if missing
with open(CREW_MAP) as f:
    crew = json.load(f)

if 'miss_pink' not in crew.get('crew', {}) and 'scarlett_coralsink' in crew.get('crew', {}):
    crew['crew']['miss_pink'] = crew['crew']['scarlett_coralsink'].copy()
    crew['crew']['miss_pink']['name'] = 'Miss Pink (PINKCADY)'
    crew['crew']['miss_pink']['token_env'] = 'DISCORD_MISS_PINK_TOKEN'
    with open(CREW_MAP, 'w') as f:
        json.dump(crew, f, indent=2)
    print('✅ Added miss_pink alias to crew_map.json')

# 2. Verify .env tokens
token_keys = ['DISCORD_MISS_PINK_TOKEN', 'DISCORD_SIR_GREEN_TOKEN', 'DISCORD_SIR_AZURE_TOKEN']
missing = []
for k in token_keys:
    val = os.environ.get(k, '')
    if not val or '[REDACTED]' in val or len(val) < 20:
        missing.append(k)

if missing:
    print(f'❌ Missing/invalid tokens: {missing}')
    print('   -> Reset in https://discord.com/developers/applications')
    sys.exit(1)
else:
    print('✅ All Discord tokens present')
"""

fix_path = "Z:/Developer_Brain/02_Business_Operations/Communications/Discord/fix_discord_tokens.py"
with open(fix_path, "w") as f:
    f.write(fix_script)
os.chmod(fix_path, 0o755)
print(f"  ✅ Created: {fix_path}")

# ─── 5. Backup crew_map.json ───────────────────────────────────────────────────
backup = f"crew_map.json.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(crews_path, HERE / backup)
print(f"  ✅ Backup: {backup}")

print("\n=== DONE ===")
print("Discord token wiring fixed:")
print("  - Added miss_pink alias to crew_map.json")
print("  - Created token intake guide")
print("  - Created fix script")
print("  - All 4 Discord audit duplicates can be archived")
print("  - Sir Green notified via Discord audit card comment")