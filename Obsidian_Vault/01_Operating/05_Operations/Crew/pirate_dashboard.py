#!/usr/bin/env python3
"""
Pirate Captain's Dashboard — PINKCADY Fleet Monitoring
Local dashboard that monitors the entire pirate fleet health and
integrates with Trello/GitHub via OODA loop.

Endpoints:
  /                    — HTML dashboard
  /api/fleet          — Fleet health summary JSON
  /api/ships          — Individual ship status
  /api/alerts         — Active alerts
  /health             — Simple health check
"""
import json
import socket
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
LOG_FILE = BASE / "10_Skills_Library/05_Operations/logs/pirate_dashboard.log"
STATE_FILE = BASE / "10_Skills_Library/05_Operations/fleet_dashboard_state.json"

# Fleet configuration
FLEET = {
    "PINKCADY": {
        "local_ip": "192.168.0.3",
        "tailscale_ip": "100.106.235.103",
        "docker_port": 2375,
        "crew_api_port": 8090,
        "role": "Torus Coffee Commander (Miss Pink)",
        "owner": "miss-pink",
        "type": "operations",
    },
    "SQUIDSTATION": {
        "local_ip": "192.168.0.39",
        "tailscale_ip": "100.83.247.14",
        "docker_port": 2375,
        "crew_api_port": 8090,
        "role": "Captain's Flagship (Sir Green)",
        "owner": "sir-green",
        "type": "flagship",
    },
    "STEALTHATTACK": {
        "local_ip": "192.168.0.10",
        "tailscale_ip": "100.110.238.68",
        "docker_port": 2375,
        "crew_api_port": 8090,
        "role": "GPU Warfare (Sir Azure)",
        "owner": "sir-azure",
        "type": "gpu",
    },
    "GATEWAY": {
        "local_ip": "192.168.0.1",
        "tailscale_ip": "192.168.0.1",
        "docker_port": 0,
        "crew_api_port": 0,
        "role": "Network Gateway",
        "owner": "shared",
        "type": "gateway",
    },
}

# Cached fleet state
fleet_state = {}
alerts = []

def log(msg: str) -> None:
    try:
        now = datetime.now(timezone.utc).isoformat()
        line = f"[{now}] {msg}"
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        pass

def check_port(ip: str, port: int, timeout: float = 3.0) -> bool:
    """Check if a TCP port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_docker_api(ts_ip: str, port: int, timeout: float = 5.0) -> dict:
    """Check Docker API accessibility and get stats."""
    try:
        import urllib.request
        url = f"http://{ts_ip}:{port}/v1.40/info"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                info = json.loads(resp.read().decode())
                return {
                    "reachable": True,
                    "version": info.get("ServerVersion", "unknown"),
                    "containers_total": info.get("Containers", 0),
                    "containers_running": info.get("ContainersRunning", 0),
                    "memory_gb": round(info.get("MemTotal", 0) / 1024 / 1024 / 1024, 1),
                }
    except Exception:
        pass
    return {"reachable": False}

def check_crew_api(ip: str, port: int, timeout: float = 3.0) -> dict:
    """Check crew_api status."""
    try:
        import urllib.request
        url = f"http://{ip}:{port}/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return {"reachable": True, "status": data.get("status", "unknown"), "ship": data.get("ship", "")}
    except Exception:
        pass
    return {"reachable": False}

def ping_host(ip: str, count: int = 1, timeout: int = 2) -> dict:
    """Ping a host and return latency."""
    try:
        r = subprocess.run(
            ["ping", "-n", str(count), "-w", str(timeout * 1000), ip],
            capture_output=True, text=True, timeout=10,
            creationflags=0x08000000
        )
        if r.returncode == 0 and "Average" in r.stdout:
            # Extract average latency from Windows ping output
            avg_str = r.stdout.split("Average = ")[1].split("ms")[0]
            return {"reachable": True, "latency_ms": float(avg_str)}
        return {"reachable": False}
    except Exception:
        return {"reachable": False}

def refresh_fleet():
    """Refresh fleet state for all ships."""
    global fleet_state, alerts
    new_state = {}
    new_alerts = []
    now = datetime.now(timezone.utc).isoformat()

    for ship_name, ship in FLEET.items():
        ship_state = {
            "name": ship_name,
            "role": ship["role"],
            "owner": ship["owner"],
            "type": ship["type"],
            "local_ip": ship["local_ip"],
            "tailscale_ip": ship["tailscale_ip"],
            "timestamp": now,
        }

        # Check ping (Tailscale IP)
        ping = ping_host(ship["tailscale_ip"])
        ship_state["ping"] = ping
        ship_state["reachable"] = ping.get("reachable", False)
        ship_state["latency_ms"] = ping.get("latency_ms", 0)

        # Check Docker API
        if ship["docker_port"] > 0:
            docker = check_docker_api(ship["tailscale_ip"], ship["docker_port"])
            ship_state["docker_api"] = docker
        else:
            ship_state["docker_api"] = {"reachable": True}  # Gateway doesn't need Docker

        # Check crew API
        if ship["crew_api_port"] > 0:
            crew = check_crew_api(ship["tailscale_ip"], ship["crew_api_port"])
            ship_state["crew_api"] = crew
        else:
            ship_state["crew_api"] = {"reachable": True}

        # Calculate health
        ports_ok = ship_state["docker_api"]["reachable"] and ship_state["crew_api"]["reachable"]
        ship_state["healthy"] = ship_state["reachable"] and ports_ok

        # Score calculation (0-20)
        score = 0
        if ship_state["reachable"]:
            score += 5
        if ship_state["docker_api"]["reachable"]:
            score += 10
        if ship_state["crew_api"]["reachable"]:
            score += 5
        ship_state["score"] = score

        # Generate alerts
        if not ship_state["reachable"]:
            new_alerts.append({
                "ship": ship_name,
                "severity": "warn",
                "type": "OFFLINE",
                "msg": f"{ship_name} not reachable via Tailscale ({ship['tailscale_ip']})",
                "ts": now,
            })
        if ship_state["reachable"] and not ship_state["docker_api"]["reachable"]:
            new_alerts.append({
                "ship": ship_name,
                "severity": "warn",
                "type": "DOCKER_API_DOWN",
                "msg": f"{ship_name} ping-ok but Docker API port {ship['docker_port']} not responding",
                "ts": now,
            })
        if ship_state["reachable"] and not ship_state["crew_api"]["reachable"]:
            new_alerts.append({
                "ship": ship_name,
                "severity": "warn",
                "type": "CREW_API_DOWN",
                "msg": f"{ship_name} ping-ok but crew_api port {ship['crew_api_port']} not responding",
                "ts": now,
            })

        new_state[ship_name] = ship_state

    fleet_state = new_state
    alerts[:] = new_alerts

    # Save state file
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({
            "fleet": fleet_state,
            "alerts": alerts,
            "timestamp": now,
        }, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass

def refresh_loop():
    """Background thread that refreshes fleet state every 10 seconds."""
    while True:
        try:
            refresh_fleet()
            log("Fleet state refreshed")
        except Exception as e:
            log(f"Refresh error: {e}")
        time.sleep(10)

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_html()
        elif self.path == "/api/fleet":
            self.send_json({"fleet": fleet_state, "alerts": alerts, "timestamp": datetime.now(timezone.utc).isoformat()})
        elif self.path == "/api/ships":
            self.send_json({"ships": fleet_state, "timestamp": datetime.now(timezone.utc).isoformat()})
        elif self.path == "/api/alerts":
            self.send_json({"alerts": alerts, "count": len(alerts), "timestamp": datetime.now(timezone.utc).isoformat()})
        elif self.path == "/health":
            self.send_json({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})
        else:
            self.send_json({"error": "not found", "path": self.path}, 404)

    def send_json(self, data, code=200):
        body = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self):
        html = self.render_html()
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def render_html(self) -> str:
        ships_html = ""
        for ship_name, s in fleet_state.items():
            status_class = "healthy" if s.get("healthy") else "unhealthy"
            status_icon = "✅" if s.get("healthy") else "❌"
            score = s.get("score", 0)
            ships_html += f"""
            <div class="ship {status_class}">
                <h2>{status_icon} {ship_name}</h2>
                <p><strong>Status:</strong> {s.get("status", s.get("ping", {}).get("reachable", False))}</p>
                <p><strong>Role:</strong> {s.get("role", "")}</p>
                <p><strong>Score:</strong> {score}/20</p>
                <p><strong>Latency:</strong> {s.get("latency_ms", "?")}ms</p>
                <details>
                    <summary>Port Details</summary>
                    <ul>
                        <li>Docker API ({s.get("local_ip", "")}:{s.get("docker_port", 2375)}): {'✅' if s.get("docker_api", {}).get("reachable") else '❌'}</li>
                        <li>Crew API (8090): {'✅' if s.get("crew_api", {}).get("reachable") else '❌'}</li>
                        <li>Local IP: {s.get("local_ip", "?")}</li>
                        <li>Tailscale: {s.get("tailscale_ip", "?")}</li>
                    </ul>
                </details>
            </div>"""

        alerts_html = ""
        if alerts:
            for a in alerts:
                alerts_html += f"""<div class="alert {a['severity']}"><strong>{a['severity'].upper()}</strong> {a['ship']}: {a['msg']}</div>"""
        else:
            alerts_html = "<div class='alert healthy'>All ships healthy! 🏴‍☠️</div>"

        return f"""<!DOCTYPE html>
<html>
<head><title>Pirate Captain's Dashboard — PINKCADY</title>
<style>
body {{ font-family: sans-serif; background: #0a0a1a; color: #e0e0ff; margin: 20px; }}
h1 {{ color: #ffaa00; }}
.ship {{ background: #111; border-radius: 8px; padding: 15px; margin: 10px 0; border-left: 3px solid #ffaa00; }}
.ship.healthy {{ border-left-color: #00ff88; }}
.ship.unhealthy {{ border-left-color: #ff4444; }}
.alert {{ padding: 8px; margin: 5px 0; border-radius: 4px; }}
.alert.warn {{ background: #332200; border-left: 3px solid #ffaa00; }}
.alert.critical {{ background: #330000; border-left: 3px solid #ff4444; }}
.alert.healthy {{ background: #003300; border-left: 3px solid #00ff88; }}
</style>
<meta http-equiv="refresh" content="10">
</head>
<body>
<h1>🏴‍☠️ Pirate Captain's Dashboard</h1>
<p>Fleet monitoring for PINKCADY, SQUIDSTATION, STEALTHATTACK, GATEWAY</p>
<h2>Fleet Status</h2>
<div id="fleet">{ships_html}</div>
<h2>Active Alerts</h2>
<div id="alerts">{alerts_html}</div>
<p><em>Auto-refreshes every 10 seconds. Data from fleet mesh sensors.</em></p>
</body>
</html>"""

    def log_message(self, format, *args):
        pass  # Suppress default logging

def main():
    log("PIRATE_DASHBOARD_STARTED — port 9091")
    
    # Start refresh thread
    t = threading.Thread(target=refresh_loop, daemon=True)
    t.start()
    
    # Initial refresh
    refresh_fleet()
    
    # Start HTTP server
    server = HTTPServer(("0.0.0.0", 9091), DashboardHandler)
    log("Listening on 0.0.0.0:9091")
    server.serve_forever()

if __name__ == "__main__":
    main()
