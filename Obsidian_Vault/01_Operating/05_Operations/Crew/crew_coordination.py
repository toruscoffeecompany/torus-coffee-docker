#!/usr/bin/env python3
"""
Crew Coordination System — Torus Coffee Company.

Prevents Miss Pink, Sir Green, and Sir Azure from working on the same
Trello card or GitHub issue simultaneously across 3 PCs:
  - PINKCADY (Miss Pink)
  - SQUIDSTATION (Sir Green)
  - STEALTHATTACK (Sir Azure)

Uses a shared lock file at Z:\Developer_Brain\Shared_With_Pink\crew_coordination_lock.json
This path is accessible from all 3 crew stations via SMB mount.

Usage in any script:
  from crew_coordination import claim_work_item, release_work_item, is_claimed

  if claim_work_item(card_id, "misspink", "working on card desc"):
      try:
          # ... do work ...
          release_work_item(card_id)
      except:
          release_work_item(card_id)
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# Shared coordination path (SMB-mounted on all crew PCs)
COORDINATION_LOCK = Path(r"Z:\Developer_Brain\Shared_With_Pink\crew_coordination_lock.json")
LOCK_BACKUP = Path(__file__).parent / "crew_coordination_lock.json"

# Station identification
STATIONS = {
    "misspink": "PINKCADY",
    "sirgreen": "SQUIDSTATION",
    "sirazure": "STEALTHATTACK",
}

# Stale claim timeout (30 min — if a station claims but goes silent, release after 30 min)
STALE_CLAIM_MINUTES = 30


def _load_lock():
    """Load the coordination lock file."""
    for path in [COORDINATION_LOCK, LOCK_BACKUP]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "claims" in data:
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"claims": {}, "version": "1.0"}


def _save_lock(data):
    """Save the coordination lock file to shared path + backup."""
    text = json.dumps(data, indent=2, ensure_ascii=False)
    for path in [COORDINATION_LOCK, LOCK_BACKUP]:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except OSError:
            pass


def claim_work_item(item_id, crew_member, description=""):
    """
    Claim a work item so other crew members don't duplicate the work.

    Returns True if claimed successfully (no one else is working on it).
    Returns False if already claimed by someone else.
    """
    with open(str(LOCK_BACKUP) + ".lock", "w") as _:
        pass  # Simple file lock via existence check
    data = _load_lock()

    # Check for stale claims
    now = datetime.now(timezone.utc)
    claims = data.get("claims", {})

    # Clean up stale claims
    stale_ids = []
    for cid, claim in claims.items():
        if cid == item_id:
            # Check if claim is stale
            claimed_at = claim.get("claimed_at", "")
            if claimed_at:
                try:
                    claimed_time = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
                    age = (now - claimed_time).total_seconds() / 60
                    if age > STALE_CLAIM_MINUTES:
                        stale_ids.append(cid)
                except (ValueError, TypeError):
                    stale_ids.append(cid)

    for cid in stale_ids:
        del claims[cid]

    # Check if already claimed (and not stale)
    if item_id in claims:
        claim = claims[item_id]
        station = STATIONS.get(claim.get("claimed_by", ""), claim.get("claimed_by", "unknown"))
        print(f"  [CREW_LOCK] {item_id}: Already claimed by {claim.get('claimed_by')} at {station}")
        return False

    # Claim it
    claims[item_id] = {
        "claimed_by": crew_member,
        "claimed_at": now.isoformat(),
        "workstation": STATIONS.get(crew_member, "UNKNOWN"),
        "description": description[:200],
    }
    data["claims"] = claims
    data["last_updated"] = now.isoformat()
    _save_lock(data)

    station = STATIONS.get(crew_member, "UNKNOWN")
    print(f"  [CREW_LOCK] {item_id}: Claimed by {crew_member} at {station}")
    return True


def release_work_item(item_id):
    """Release a work item claim."""
    data = _load_lock()
    claims = data.get("claims", {})
    if item_id in claims:
        claim = claims.pop(item_id, None)
        data["claims"] = claims
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        _save_lock(data)
        if claim:
            print(f"  [CREW_LOCK] {item_id}: Released by {claim.get('claimed_by')}")
    else:
        print(f"  [CREW_LOCK] {item_id}: No active claim to release")


def is_claimed(item_id):
    """Check if a work item is currently claimed."""
    data = _load_lock()
    claims = data.get("claims", {})
    if item_id in claims:
        claim = claims[item_id]
        # Check staleness
        now = datetime.now(timezone.utc)
        try:
            claimed_time = datetime.fromisoformat(claim.get("claimed_at", "").replace("Z", "+00:00"))
            age = (now - claimed_time).total_seconds() / 60
            if age > STALE_CLAIM_MINUTES:
                return False  # Stale — treat as unclaimed
        except (ValueError, TypeError):
            pass
        return True
    return False


def list_claims():
    """List all current work claims."""
    data = _load_lock()
    claims = data.get("claims", {})
    now = datetime.now(timezone.utc)

    active = []
    for item_id, claim in claims.items():
        claimed_at = claim.get("claimed_at", "")
        try:
            claimed_time = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
            age_min = (now - claimed_time).total_seconds() / 60
        except (ValueError, TypeError):
            age_min = -1

        if age_min > STALE_CLAIM_MINUTES:
            continue  # Skip stale

        active.append({
            "item_id": item_id,
            "claimed_by": claim.get("claimed_by", "unknown"),
            "workstation": claim.get("workstation", "UNKNOWN"),
            "description": claim.get("description", "")[:50],
            "age_minutes": round(age_min, 1),
        })

    return active


def print_claim_status():
    """Print current claim status for debugging."""
    claims = list_claims()
    if not claims:
        print("[CREW_LOCK] No active work claims — all clear")
        return

    print(f"[CREW_LOCK] {len(claims)} active claims:")
    for c in claims:
        print(f"  {c['item_id'][:8]}: {c['claimed_by']} @ {c['workstation']} "
              f"({c['age_minutes']:.0f} min ago) — {c['description']}")


if __name__ == "__main__":
    print_claim_status()
