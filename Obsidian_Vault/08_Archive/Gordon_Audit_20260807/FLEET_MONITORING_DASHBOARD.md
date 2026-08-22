# ⚓ FLEET MONITORING DASHBOARD
## Real-time Web UI for Captain

**Purpose:** Captain sees all 3 ships on one web page with live metrics  
**Language:** Python (Flask) + JavaScript (frontend)  
**Port:** 5000 (localhost on PINKCADY or accessible via Tailscale)  
**Deployment:** Single container or systemd service

---

## Installation

```bash
# On PINKCADY
pip install flask flask-cors requests prometheus-client

# Create directory
mkdir -p /opt/fleet-dashboard
cd /opt/fleet-dashboard

# Copy files
cp fleet_dashboard.py /opt/fleet-dashboard/
cp fleet_dashboard.html /opt/fleet-dashboard/templates/
cp fleet_dashboard.css /opt/fleet-dashboard/static/

# Run
python fleet_dashboard.py
# Access: http://localhost:5000 or http://100.106.235.103:5000 (from Tailscale)
```

---

## Code: Backend (Flask)

```python
#!/usr/bin/env python3
"""
Fleet Monitoring Dashboard - Real-time metrics for all 3 ships
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
from threading import Thread
import time

app = Flask(__name__)
CORS(app)

# Fleet configuration
FLEET = {
    "SQUIDSTATION": {"ip": "100.83.247.14", "docker_port": 2375, "type": "flagship"},
    "PINKCADY": {"ip": "100.106.235.103", "docker_port": 2375, "type": "operations"},
    "STEALTHATTACK": {"ip": "100.110.238.68", "docker_port": 2375, "type": "gpu"}
}

# Cached metrics
metrics_cache = {}

def get_docker_stats(ship_name, ship_config):
    """Get Docker stats from a ship"""
    try:
        docker_api = f"http://{ship_config['ip']}:{ship_config['docker_port']}"
        
        # Get containers
        resp = requests.get(f"{docker_api}/v1.40/containers/json", timeout=5)
        containers = resp.json() if resp.status_code == 200 else []
        
        # Get system info
        info_resp = requests.get(f"{docker_api}/v1.40/info", timeout=5)
        info = info_resp.json() if info_resp.status_code == 200 else {}
        
        # Aggregate stats
        total_memory = 0
        running_containers = 0
        
        for container in containers:
            if container["State"] == "running":
                running_containers += 1
        
        return {
            "ship": ship_name,
            "type": ship_config["type"],
            "reachable": True,
            "containers_total": len(containers),
            "containers_running": running_containers,
            "containers_stopped": len(containers) - running_containers,
            "driver": info.get("Driver", "unknown"),
            "kernel_version": info.get("KernelVersion", "unknown"),
            "os": info.get("OperatingSystem", "unknown")
        }
    except Exception as e:
        return {
            "ship": ship_name,
            "type": ship_config["type"],
            "reachable": False,
            "error": str(e)
        }

def get_prometheus_metrics(ship_name):
    """Get Prometheus metrics"""
    try:
        if "SQUIDSTATION" in ship_name:
            prometheus_url = "http://100.83.247.14:9090"
        else:
            prometheus_url = "http://100.106.235.103:9090"
        
        queries = {
            "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total[5m])) by (container_label_com_docker_compose_service)',
            "memory_usage": 'sum(container_memory_usage_bytes) by (container_label_com_docker_compose_service) / 1024 / 1024',
            "disk_usage": 'node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"}'
        }
        
        results = {}
        for query_name, query in queries.items():
            resp = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=5
            )
            if resp.status_code == 200:
                results[query_name] = resp.json()
        
        return results
    except Exception as e:
        return {"error": str(e)}

def refresh_metrics():
    """Background thread to refresh metrics every 10 seconds"""
    while True:
        try:
            for ship_name, ship_config in FLEET.items():
                stats = get_docker_stats(ship_name, ship_config)
                metrics = get_prometheus_metrics(ship_name)
                
                metrics_cache[ship_name] = {
                    "stats": stats,
                    "metrics": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error refreshing metrics: {e}")
        
        time.sleep(10)

@app.route("/")
def index():
    """Render dashboard"""
    return render_template("fleet_dashboard.html")

@app.route("/api/fleet-status")
def fleet_status():
    """Get status of all ships"""
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "ships": metrics_cache
    })

@app.route("/api/ship/<ship_name>")
def ship_detail(ship_name):
    """Get detailed info for a ship"""
    if ship_name in metrics_cache:
        return jsonify(metrics_cache[ship_name])
    return jsonify({"error": "Ship not found"}), 404

@app.route("/api/alerts")
def get_alerts():
    """Get recent alerts"""
    try:
        resp = requests.get("http://100.106.235.103:4000/alerts?limit=20", timeout=5)
        return jsonify(resp.json())
    except:
        return jsonify({"alerts": []})

@app.route("/api/health")
def health():
    """Health check"""
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    # Start metrics refresh in background
    metrics_thread = Thread(target=refresh_metrics, daemon=True)
    metrics_thread.start()
    
    # Start Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)
```

---

## Code: Frontend (HTML + JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
    <title>⚓ Fleet Monitoring Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='fleet_dashboard.css') }}">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>⚓ Pirate Fleet Dashboard</h1>
        <p>Real-time monitoring of all 3 ships</p>
    </div>
    
    <div class="container">
        <!-- Fleet Overview -->
        <div class="section">
            <h2>Fleet Status</h2>
            <div class="fleet-grid" id="fleet-grid">
                <!-- Dynamically populated -->
            </div>
        </div>
        
        <!-- Alerts -->
        <div class="section">
            <h2>Recent Alerts</h2>
            <div class="alerts-container" id="alerts">
                <!-- Dynamically populated -->
            </div>
        </div>
        
        <!-- Charts -->
        <div class="section">
            <h2>Metrics</h2>
            <div class="charts">
                <div class="chart-container">
                    <canvas id="cpu-chart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="memory-chart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Fetch fleet status
        async function updateDashboard() {
            try {
                const response = await fetch('/api/fleet-status');
                const data = await response.json();
                
                // Update fleet grid
                const grid = document.getElementById('fleet-grid');
                grid.innerHTML = '';
                
                for (const [ship_name, ship_data] of Object.entries(data.ships)) {
                    const stats = ship_data.stats || {};
                    const html = `
                        <div class="ship-card ${stats.reachable ? 'online' : 'offline'}">
                            <h3>${stats.ship}</h3>
                            <p class="type">${stats.type}</p>
                            <div class="status">${stats.reachable ? '✓ ONLINE' : '✗ OFFLINE'}</div>
                            <div class="metrics">
                                <p>Containers: ${stats.containers_running}/${stats.containers_total}</p>
                                <p>OS: ${stats.os}</p>
                            </div>
                        </div>
                    `;
                    grid.innerHTML += html;
                }
                
                // Update alerts
                const alertsResp = await fetch('/api/alerts');
                const alertsData = await alertsResp.json();
                const alertsDiv = document.getElementById('alerts');
                alertsDiv.innerHTML = alertsData.alerts.slice(0, 5).map(alert => `
                    <div class="alert ${alert.severity}">
                        <span class="time">${alert.timestamp}</span>
                        <span class="service">${alert.service}</span>
                        <span class="message">${alert.message}</span>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        // Update dashboard every 10 seconds
        updateDashboard();
        setInterval(updateDashboard, 10000);
    </script>
</body>
</html>
```

---

## Code: CSS Styling

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Courier New', monospace;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #fff;
    line-height: 1.6;
}

.header {
    background: rgba(0, 0, 0, 0.5);
    padding: 2rem;
    text-align: center;
    border-bottom: 3px solid #00ff00;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.container {
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.section {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid #00ff00;
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 2rem;
}

.section h2 {
    color: #00ff00;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

.fleet-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.ship-card {
    background: rgba(0, 255, 0, 0.05);
    border: 2px solid #00ff00;
    border-radius: 8px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.ship-card.online {
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
}

.ship-card.offline {
    border-color: #ff0000;
    opacity: 0.5;
}

.ship-card h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
}

.ship-card .type {
    color: #00aaff;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.ship-card .status {
    padding: 0.5rem;
    margin-bottom: 1rem;
    background: rgba(0, 255, 0, 0.1);
    border-radius: 4px;
    font-weight: bold;
}

.ship-card .metrics p {
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.alerts-container {
    max-height: 400px;
    overflow-y: auto;
}

.alert {
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid;
    background: rgba(255, 255, 255, 0.05);
}

.alert.critical {
    border-left-color: #ff0000;
    background: rgba(255, 0, 0, 0.1);
}

.alert.warning {
    border-left-color: #ffaa00;
    background: rgba(255, 170, 0, 0.1);
}

.alert.info {
    border-left-color: #00aaff;
    background: rgba(0, 170, 255, 0.1);
}

.charts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}

.chart-container {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 1rem;
}
```

---

## Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fleet_dashboard.py .
COPY templates/ templates/
COPY static/ static/

EXPOSE 5000

CMD ["python", "fleet_dashboard.py"]
```

```bash
# Build and run
docker build -t fleet-dashboard .
docker run -d -p 5000:5000 --name fleet-dashboard fleet-dashboard
```

---

## Features

✅ Real-time fleet status (all 3 ships)  
✅ Container metrics per ship  
✅ Alert feed  
✅ Beautiful web UI  
✅ Responsive design  
✅ Live updates every 10s  
✅ Tailscale accessible  

---

⚓ **Miss Gordon**

This dashboard runs independently on PINKCADY, doesn't touch Miss Pink's infrastructure, and gives Captain a complete overview of all 3 ships in one web page.

Want me to code more? 🚀
