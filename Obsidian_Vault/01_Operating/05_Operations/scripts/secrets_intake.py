#!/usr/bin/env python3
"""
Secrets Intake Validator — Torus Coffee Company
Validates Discord webhook, Gmail app password, and backup path formats.
Does NOT store plaintext secrets. Only reports validity, masked values, and hashes.
OPSEC: If a secret is invalid, the admin must re-enter it via secure handoff.
"""
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
REPORT_PATH = VAULT / "10_Skills_Library" / "05_Operations" / "logs" / "secrets_intake_report.json"

DISCORD_WEBHOOK_RE = re.compile(
    r"^https://(discord|discordapp)\.com/api/webhooks/\d+/[\w-]{40,}$"
)
GMAIL_APP_PASSWORD_RE = re.compile(r"^[a-z]{4} [a-z]{4} [a-z]{4} [a-z]{4}$")
BACKUP_PATH_RE = re.compile(r"^[a-zA-Z]:\\[^<>:\"|?*\x00-\x1F]+$|^[a-zA-Z]:/[^<>:\"|?*\x00-\x1F]+$")


def mask(secret: str, keep: int = 4) -> str:
    if not secret:
        return ""
    if len(secret) <= keep * 2:
        return "*" * len(secret)
    return f"{secret[:keep]}...{secret[-keep:]}"


def hash_secret(secret: str) -> str:
    if not secret:
        return ""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:16]


def validate_discord_webhook(value: str) -> dict:
    value = value.strip()
    if not value:
        return {"valid": False, "error": "Webhook URL is empty"}
    if not DISCORD_WEBHOOK_RE.match(value):
        return {"valid": False, "error": "Format must be https://discord.com/api/webhooks/<id>/<token>"}
    return {
        "valid": True,
        "masked": mask(value),
        "hash": hash_secret(value),
        "error": None,
    }


def validate_gmail_app_password(value: str) -> dict:
    value = value.strip().lower()
    if not value:
        return {"valid": False, "error": "App password is empty"}
    # Gmail app passwords are 16 lowercase alphanumeric chars with spaces
    if not GMAIL_APP_PASSWORD_RE.match(value):
        return {"valid": False, "error": "Format must be 16 chars in 4 groups (abcd efgh ijkl mnop)"}
    return {
        "valid": True,
        "masked": mask(value.replace(" ", "")),
        "hash": hash_secret(value),
        "error": None,
    }


def validate_backup_path(value: str) -> dict:
    value = value.strip().strip('"').strip("'")
    if not value:
        return {"valid": False, "error": "Backup path is empty"}
    p = Path(value)
    if not p.drive:
        return {"valid": False, "error": "Path must include a drive letter (e.g. D:/backups)"}
    if BACKUP_PATH_RE.match(value):
        return {
            "valid": True,
            "masked": str(p.parent / mask(p.name, keep=1)) if p.name else value,
            "hash": hash_secret(value),
            "error": None,
        }
    return {"valid": False, "error": "Invalid path format or contains forbidden characters"}


def write_report(report: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        import json
        json.dump(report, f, indent=2)
    print(f"[OK] Report written to: {REPORT_PATH}")


def main():
    import sys

    print("=" * 60)
    print("TORUS COFFEE COMPANY — SECRETS INTAKE VALIDATOR")
    print("OPSEC: No plaintext secrets are stored.")
    print("=" * 60)
    print()

    if len(sys.argv) == 3:
        # Non-interactive mode: secrets_intake.py discord "<url>"
        mode = sys.argv[1]
        value = sys.argv[2]
        if mode == "discord":
            result = validate_discord_webhook(value)
        elif mode == "gmail":
            result = validate_gmail_app_password(value)
        elif mode == "backup":
            result = validate_backup_path(value)
        else:
            print(f"Unknown mode: {mode}")
            sys.exit(1)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)

    # Interactive mode
    results = {}
    results["timestamp"] = datetime.now(timezone.utc).isoformat()
    results["secrets"] = {}

    # Discord
    print("STEP 1/3 — Discord Webhook URL")
    print("  Find it in Discord: Server Settings ^ Integrations ^ Webhooks")
    dw = input("  Paste webhook URL: ").strip()
    results["secrets"]["discord_webhook"] = validate_discord_webhook(dw)
    v = results["secrets"]["discord_webhook"]["valid"]
    print(f"  Result: {'VALID' if v else 'INVALID'} | Masked: {mask(dw)}")
    if not v:
        print(f"  Error: {results['secrets']['discord_webhook']['error']}")
    print()

    # Gmail
    print("STEP 2/3 — Gmail App Password")
    print("  Generate at https://myaccount.google.com/apppasswords")
    gp = input("  Paste 16-char app password: ").strip()
    results["secrets"]["gmail_app_password"] = validate_gmail_app_password(gp)
    v = results["secrets"]["gmail_app_password"]["valid"]
    print(f"  Result: {'VALID' if v else 'INVALID'} | Masked: {mask(gp.replace(' ', ''))}")
    if not v:
        print(f"  Error: {results['secrets']['gmail_app_password']['error']}")
    print()

    # Backup path
    print("STEP 3/3 — Backup Path")
    print("  Recommended: D:/backups or Z:/backups")
    bp = input("  Enter backup path: ").strip()
    results["secrets"]["backup_path"] = validate_backup_path(bp)
    v = results["secrets"]["backup_path"]["valid"]
    print(f"  Result: {'VALID' if v else 'INVALID'} | Masked: {results['secrets']['backup_path']['masked']}")
    if not v:
        print(f"  Error: {results['secrets']['backup_path']['error']}")
    print()

    all_valid = all(s.get("valid") for s in results["secrets"].values())
    results["all_valid"] = all_valid
    print("=" * 60)
    print(f"Overall: {'ALL SECRETS VALID — ready for handoff' if all_valid else 'SOME SECRETS INVALID — please retry'}")
    print("=" * 60)

    write_report(results)
    return 0 if all_valid else 1


if __name__ == "__main__":
    import json
    exit(main())
