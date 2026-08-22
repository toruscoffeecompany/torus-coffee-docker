#!/usr/bin/env python3
"""Torus Coffee Company Dashboard API — Crew status, vault sync, Trello integration."""
from flask import Flask, jsonify
import requests
import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("torus-dashboard")

app = Flask(__name__)

VAULT_BASE = Path(r"D:\Work\Torus Coffee Company LLC")
TRELLO_CRED_FILE = VAULT_BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"

SERVICES = {
    "torus-pos": "http://torus-pos:3100",
    "torus-inventory": "http://torus-inventory:3200",
    "torus-redis": "tcp://torus-redis:6379",
}


def load_trello_creds():
    """Extract Trello API key + token from credentials markdown."""
    try:
        text = TRELLO_CRED_FILE.read_text(errors="ignore")
        lines = text.splitlines()
        api_key = token = None
        for i, line in enumerate(lines):
            if "API Key" in line and i + 1 < len(lines):
                api_key = lines[i + 1].strip().strip("`")
            elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
                token = lines[i + 1].strip().strip("`")
        if api_key and token:
            return api_key, token
    except Exception:
        pass
    return None, None


@app.route("/")
def index():
    return jsonify({"service": "torus-dashboard", "status": "ok"})


@app.route("/health")
def health():
    return {"status": "ok", "service": "torus-dashboard"}


@app.route("/status")
def status():
    results = {}
    for name, url in SERVICES.items():
        try:
            if url.startswith("tcp://"):
                # TCP socket check for non-HTTP services (e.g., Redis)
                import socket as _sock
                host = url.replace("tcp://", "").split(":")[0]
                port = int(url.split(":")[-1])
                s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, port))
                s.close()
                results[name] = {"status": "healthy", "type": "tcp", "port": port}
            else:
                r = requests.get(f"{url}/health", timeout=2)
                results[name] = {"status": "healthy", "code": r.status_code}
        except Exception as e:
            results[name] = {"status": "unhealthy", "error": str(e)}
    return jsonify(results)

@app.route("/vault-sync")
def vault_sync():
    """Vault sync status widget — checks git status + crew state files."""
    result = {
        "vault_root": str(VAULT_BASE),
        "git_dirty": False,
        "dirty_files": 0,
        "crew_state_files": {},
        "services": {},
    }

    # Check git status
    try:
        r = subprocess.run(
            ["git", "-C", str(VAULT_BASE), "status", "--porcelain"],
            capture_output=True, text=True, timeout=15
        )
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        result["dirty_files"] = len(lines)
        result["git_dirty"] = len(lines) > 0
        result["dirty_file_list"] = lines[:10]  # first 10
    except Exception as e:
        result["git_error"] = str(e)

    # Check crew state files
    state_dir = VAULT_BASE / "10_Skills_Library" / "05_Operations"
    for name in ["master_ooda_loop_state.json", "smart_ticket_cycle_state.json",
                  "continuous_ooda_state.json", "Crew/CREW_QUEUE_STATE.json"]:
        fpath = state_dir / name
        if fpath.exists():
            try:
                import time as _time
                mtime = fpath.stat().st_mtime
                result["crew_state_files"][name] = {
                    "exists": True,
                    "last_modified": _time.ctime(mtime),
                    "size_bytes": fpath.stat().st_size,
                }
            except Exception:
                result["crew_state_files"][name] = {"exists": True, "error": str(e)}
        else:
            result["crew_state_files"][name] = {"exists": False}

    # Check Docker services
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}} {{.Status}}"],
            capture_output=True, text=True, timeout=10, cwd=str(VAULT_BASE)
        )
        services = {}
        for line in r.stdout.strip().splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2:
                services[parts[0]] = parts[1]
        result["services"] = services
    except Exception as e:
        result["docker_error"] = str(e)

    return jsonify(result)


@app.route("/trello")
def trello_board():
    """Trello board widget — returns card counts by list/priority."""
    api_key, token = load_trello_creds()
    if not api_key or not token:
        return jsonify({"error": "Trello credentials not found"}), 500

    board_id = "6a70a3157d0db4214ac3f9a3"  # Torus_Ops board
    result = {
        "boards": [],
        "total_cards": 0,
        "priority_breakdown": {},
    }

    try:
        # Get list names
        r = requests.get(
            f"https://api.trello.com/1/boards/{board_id}/lists",
            params={"key": api_key, "token": token, "fields": "name"},
            timeout=15
        )
        lists = r.json()
        list_map = {l["id"]: l["name"] for l in lists}

        # Get open cards
        r2 = requests.get(
            f"https://api.trello.com/1/boards/{board_id}/cards",
            params={"key": api_key, "token": token, "fields": "name,idList"},
            timeout=15
        )
        cards = r2.json()
        result["total_cards"] = len(cards)

        # Group by list
        by_list = {}
        priority_breakdown = {}
        for card in cards:
            list_name = list_map.get(card["idList"], "Unknown")
            by_list[list_name] = by_list.get(list_name, 0) + 1

            # Extract priority from list name
            if "Top 10" in list_name:
                priority_breakdown["Top10"] = priority_breakdown.get("Top10", 0) + 1
            elif "P0" in list_name:
                priority_breakdown["P0"] = priority_breakdown.get("P0", 0) + 1
            elif "P1" in list_name:
                priority_breakdown["P1"] = priority_breakdown.get("P1", 0) + 1
            elif "P2" in list_name:
                priority_breakdown["P2"] = priority_breakdown.get("P2", 0) + 1
            elif "P3" in list_name:
                priority_breakdown["P3"] = priority_breakdown.get("P3", 0) + 1
            elif "Done" in list_name:
                priority_breakdown["Done"] = priority_breakdown.get("Done", 0) + 1

        result["lists"] = by_list
        result["priority_breakdown"] = priority_breakdown

    except Exception as e:
        result["error"] = str(e)

    return jsonify(result)


@app.route("/github")
def github_status():
    """GitHub issue status widget — counts open issues per repo."""
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    repos = ["toruscoffeecompany/Torus_Ops", "toruscoffeecompany/torus-coffee-docker",
             "toruscoffeecompany/Torus_website_rebuild"]
    result = {"repos": {}}
    headers = {"Accept": "application/vnd.github+json"}
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"

    for repo in repos:
        try:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/issues",
                params={"state": "open", "per_page": 100},
                headers=headers, timeout=15
            )
            if r.status_code == 200:
                result["repos"][repo] = len(r.json())
            else:
                result["repos"][repo] = {"error": r.status_code}
        except Exception as e:
            result["repos"][repo] = {"error": str(e)}

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
