#!/usr/bin/env python3
"""Recurring GitHub issue audit + labeler aligned with Trello priority taxonomy."""
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
SECRETS_FILE = BASE / "10_Skills_Library" / "05_Operations" / "secrets.local.json"
SNAPSHOT_FILE = BASE / "10_Skills_Library" / "05_Operations" / "AUDIT_SNAPSHOT.json"
OODA_FILE = BASE / "10_Skills_Library" / "05_Operations" / "OODA_TASK_LIST.md"
REPO = "toruscoffeecompany/Torus_Ops"

gh_token = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))["github_token"]


def classify(title: str, body: str = "") -> str:
    t = (title + " " + body).lower()
    if any(k in t for k in [
        "alert", "blocked", "403", "502", "critical", "emergency", "security", "breach", "down", "outage", "🚨"
    ]):
        return "P0"
    if any(k in t for k in [
        "freeze-dried production", "square developer", "payments live", "pos deployment",
        "inventory deployment", "website launch", "production sop", "revenue stream plan",
        "first sale", "confirm pat works", "github auth for toruscoffeecompany repos",
        "first dollar", "first paid"
    ]):
        return "Top 10"
    if any(k in t for k in [
        "future", "ai answering", "phone number", "sms", "text automation", "google voice",
        "research free", "evaluate ai", "voice ai receptionist", "ar menu preview",
        "q1 2027", "2027", "2028", "paid upgrade", "after revenue proof", "someday",
        "next year", "future campaign", "new year new", "halloween", "christmas", "thanksgiving"
    ]):
        return "Future Ideas"
    if any(k in t for k in [
        "sir azure", "sirazure", "nikto", "tshark", "yara", "squidstation", "security tools"
    ]):
        return "Sir Azure"
    if any(k in t for k in [
        "sir green", "sirgreen", "docker", "dashboard", "api/", "build docker", "fleet", "swarm", "compose"
    ]):
        return "Sir Green"
    if any(k in t for k in [
        "launch", "deploy", "go live", "critical fix", "urgent", "asap", "this week", "must do",
        "blocking", "blocker", "dependency", "first issue", "setup github repos", "setup github",
        "create first", "confirm pat", "test pat", "auth broken", "github connection",
        "miss pink github", "get github", "github username", "github auth"
    ]):
        return "P1"
    if any(k in t for k in [
        "build", "create", "implement", "integrate", "connect", "design", "write", "develop",
        "test", "verify", "validate", "update", "configure", "fix", "debug", "optimize", "improve"
    ]):
        return "P2"
    if any(k in t for k in [
        "follow", "email", "graphics", "template", "content", "signature", "research",
        "investigate", "review", "audit", "plan", "analyze", "content -", "website content",
        "social post", "schedule", "track ", "monitor", "report", "update doc", "document",
        "discord bot", "bot script", "keep live", "maintenance", "weekly", "monthly",
        "inventory count", "count"
    ]):
        return "P3"
    if any(k in t for k in [
        "backlog", "later", "maybe", "park", "hold", "someday", "polish", "cleanup",
        "refactor", "renovate", "redesign", "enhancement", "nice to have", "optional",
        "future improvement", "graphics", "banner", "logo", "branding", "template design"
    ]):
        return "P4"
    if any(k in t for k in [
        "assess", "evaluate", "validate", "check", "approval", "review needed",
        "review required", "decision needed", "approval needed", "get ", "confirm ",
        "verify ", "check if", "find out", "username", "credential", "access", "account"
    ]):
        return "P5"
    if any(k in t for k in [
        "blocked", "waiting", "dependency", "external", "waiting on", "blocked by",
        "seasonal", "campaign", "q1 2027", "q2 2027", "q3 2027", "q4 2027",
        "2027", "2028", "next year", "future campaign", "new year new", "halloween",
        "christmas", "thanksgiving", "easter", "valentine", "mothers day", "fathers day",
        "black friday", "cyber monday"
    ]):
        return "P6"
    return "P3"


def main() -> int:
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100",
        headers={"Authorization": f"token {gh_token}"},
        timeout=15,
    )
    issues = r.json()
    tagged = 0
    applied = {}
    errors = []

    expected = {"P0", "Top 10", "P1", "P2", "P3", "P4", "P5", "P6", "Future Ideas", "Sir Azure", "Sir Green"}
    for i in issues:
        labels = [l["name"] for l in i.get("labels", [])]
        pri = classify(i.get("title", ""), i.get("body", "") or "")
        if pri in labels:
            applied.setdefault("skipped", 0)
            applied["skipped"] += 1
            continue
        payload_labels = [pri]
        if "Top 10" not in labels and pri == "Top 10":
            payload_labels.append("Top 10")
        r2 = requests.post(
            f"https://api.github.com/repos/{REPO}/issues/{i['number']}/labels",
            json={"labels": payload_labels},
            headers={
                "Authorization": f"token {gh_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15,
        )
        if r2.status_code == 200:
            tagged += 1
            applied.setdefault(pri, 0)
            applied[pri] += 1
        else:
            errors.append(f"{i['number']}: {r2.status_code} {r2.text}")

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "github_total_open": len(issues),
        "github_retagged": tagged,
        "github_label_distribution": applied,
        "errors": errors,
        "next_actions": [
            "Mirror priority labels from Trello to GitHub issues on creation",
            "Sync queue assignments between Trello queues and GitHub issue metadata",
            "Run full automation audit for inbox -> GitHub -> Trello -> indexing path",
        ],
    }
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"AUDIT_OK retagged={tagged} total={len(issues)} distribution={applied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
