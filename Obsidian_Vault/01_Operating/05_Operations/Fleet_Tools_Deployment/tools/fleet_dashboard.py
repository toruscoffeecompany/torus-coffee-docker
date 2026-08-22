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