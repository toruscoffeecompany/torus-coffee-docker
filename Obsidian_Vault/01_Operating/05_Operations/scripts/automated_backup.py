#!/usr/bin/env python3
"""
Automated Backup — Torus Coffee Company
Free-tier/local-only backup of vault docs and local SQLite DB.
Writes backup report to `logs/backup_report.json`.
"""
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DB_PATH = VAULT / "10_Skills_Library" / "05_Operations" / "data" / "torus_local.db"
LOG_FILE = VAULT / "10_Skills_Library" / "05_Operations" / "logs" / "backup_report.json"
DEFAULT_BACKUP_DIR = VAULT / "backups"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_report() -> dict:
    try:
        if LOG_FILE.exists():
            return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"runs": []}


def save_report(report: dict) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"BACKUP_REPORT_SAVE_FAIL {exc}")


def backup_db(dest_dir: Path) -> dict:
    result = {"type": "sqlite", "source": str(DB_PATH)}
    try:
        if not DB_PATH.exists():
            return {**result, "status": "skipped", "reason": "missing_db"}
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "torus_local.db"
        shutil.copy2(str(DB_PATH), str(dest))
        conn = sqlite3.connect(dest)
        conn.execute("PRAGMA integrity_check")
        conn.close()
        return {**result, "status": "ok", "dest": str(dest)}
    except Exception as exc:
        return {**result, "status": "error", "error": str(exc)}


def backup_vault_docs(dest_dir: Path) -> dict:
    result = {"type": "vault_docs", "source": str(VAULT)}
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for root, dirs, files in os.walk(str(VAULT)):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".next"}]
            for file in files:
                src = Path(root) / file
                rel = src.relative_to(VAULT)
                dst = dest_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                    continue
                shutil.copy2(str(src), str(dst))
                copied += 1
        return {**result, "status": "ok", "copied_files": copied}
    except Exception as exc:
        return {**result, "status": "error", "error": str(exc)}


def main() -> int:
    print("=" * 60)
    print("AUTOMATED BACKUP")
    print("=" * 60)
    report = load_report()
    run_at = now_iso()
    backup_root = DEFAULT_BACKUP_DIR / run_at.replace(":", "-").replace("+", "z")
    db_result = backup_db(backup_root / "db")
    docs_result = backup_vault_docs(backup_root / "vault")
    run = {
        "run_at": run_at,
        "backup_root": str(backup_root),
        "db": db_result,
        "vault_docs": docs_result,
    }
    report["runs"].append(run)
    report.setdefault("latest", run)
    save_report(report)
    print(f"✓ DB backup: {db_result.get('status')}")
    print(f"✓ Vault docs backup: {docs_result.get('status')}")
    print(f"✓ Backup root: {backup_root}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
