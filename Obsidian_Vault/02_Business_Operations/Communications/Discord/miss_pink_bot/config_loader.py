import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECRETS_LOCAL = ROOT / "secrets.local.json"
SECRETS_ENV = os.environ.get("MISS_PINK_BOT_SECRETS")


def load_secrets() -> dict:
    try:
        if SECRETS_ENV and Path(SECRETS_ENV).exists():
            return json.loads(Path(SECRETS_ENV).read_text(encoding="utf-8"))
        if SECRETS_LOCAL.exists():
            return json.loads(SECRETS_LOCAL.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def get_secret(name: str, default: str = "") -> str:
    return os.environ.get(name, load_secrets().get(name, default))
