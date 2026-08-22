#!/usr/bin/env python3
"""
TOOL AE: Crew Status Dashboard
Web UI showing all 3 ships status in real-time (localhost:6000)
"""

from flask import Flask, render_template_string, jsonify
import requests
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

class FleetStatusManager:
    def __init__(self):
        self.ships = {
            "Sir Green": {
                "ship_name": "SQUIDSTATION",
                "ip": "100.83.247.14",
                "role": "Infrastructure",
                "status": "unknown"
            },
            "Miss Pink": {
                "ship_name": "PINKCADY",
                "ip": "100.106.235.103",
                "role": "Operations Hub",
                "status": "unknown"
            },
            "Sir Azure": {
                "ship_name": "STEALTHATTACK",
                "ip": "100.110.238.68",
                "role": "GPU/AI Pipeline",
                "status": "unknown"
            }
        }
        self.status_log = Path("/data/fleet_status_history.json")
        self.status_log.parent.mkdir(exist_ok=True)
    
    def check_ship_status(self, ship_name, ship_ip):
        """Check if ship is online"""
        try:
            response = requests.get(f"http://{ship_ip}:2375/_ping", timeout=2)
            return "online" if response.status_code == 200 else "offline"
        except:
            return "offline"
    
    def get_all_status(self):
        """Get status of all ships"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "ships": {},
            "fleet_status": "operational"
        }
        
        online_count = 0
        
        for crew_member, info in self.ships.items():
            ship_status = self.check_ship_status(info["ship_name"], info["ip"])
            status["ships"][crew_member] = {
                "ship_name": info["ship_name"],
                "ip": info["ip"],
                "role": info["role"],
                "status": ship_status
            }
            
            if ship_status == "online":
                online_count += 1
        
        # Determine fleet status
        if online_count == 3:
            status["fleet_status"] = "operational"
        elif online_count >= 2:
            status["fleet_status"] = "degraded"
        else:
            status["fleet_status"] = "critical"
        
        # Log status
        try:
            with open(self.status_log, 'a') as f:
                f.write(json.dumps(status) + "\n")
        except:
            pass
        
        return status

manager = FleetStatusManager()

@app.route("/")
def dashboard():
    """Main dashboard"""
    status = manager.get_all_status()
    
    fleet_icon = {
        "operational": "✅",
        "degraded": "⚠️",
        "critical": "🚨"
    }
    
    fleet_color = {
        "operational": "#00ff00",
        "degraded": "#ffff00",
        "critical": "#ff0000"
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏴‍☠️ Pirate Fleet Status</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Monaco', 'Courier New', monospace;
                background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
                color: #e0e0e0;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ 
                text-align: center; 
                color: #ffd700; 
                margin-bottom: 10px;
                font-size: 2.5em;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            }}
            .fleet-status {{
                text-align: center;
                margin-bottom: 30px;
                padding: 15px;
                background: rgba(255, 215, 0, 0.1);
                border-radius: 10px;
                border: 2px solid #ffd700;
            }}
            .fleet-status-text {{
                font-size: 1.2em;
                color: {fleet_color[status['fleet_status']]};
                font-weight: bold;
            }}
            .ships {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .ship-card {{ 
                border: 3px solid #ffd700; 
                border-radius: 15px; 
                padding: 25px; 
                background: rgba(26, 31, 58, 0.8);
                backdrop-filter: blur(10px);
                transition: transform 0.3s, box-shadow 0.3s;
                cursor: pointer;
            }}
            .ship-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            }}
            .ship-name {{ 
                font-size: 20px; 
                font-weight: bold; 
                color: #ffd700; 
                margin-bottom: 10px;
                text-transform: uppercase;
            }}
            .ship-role {{
                color: #888;
                font-size: 12px;
                margin-bottom: 15px;
            }}
            .ship-info {{
                margin: 8px 0;
                font-size: 14px;
                color: #ccc;
            }}
            .ship-info-label {{
                color: #ffd700;
                font-weight: bold;
            }}
            .status-online {{ 
                color: #00ff00; 
                font-weight: bold;
            }}
            .status-offline {{ 
                color: #ff0000; 
                font-weight: bold;
            }}
            .timestamp {{ 
                font-size: 11px; 
                color: #666; 
                text-align: center; 
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #333;
            }}
            .refresh-info {{
                text-align: center;
                color: #888;
                font-size: 12px;
                margin-top: 20px;
            }}
        </style>
        <meta http-equiv="refresh" content="5">
    </head>
    <body>
        <div class="container">
            <h1>🏴‍☠️ PIRATE FLEET STATUS</h1>
            
            <div class="fleet-status">
                <div class="fleet-status-text">
                    {fleet_icon[status['fleet_status']]} Fleet Status: {status['fleet_status'].upper()}
                </div>
            </div>
            
            <div class="ships">
    """
    
    for crew_member, info in status["ships"].items():
        status_class = "status-online" if info["status"] == "online" else "status-offline"
        status_icon = "✅" if info["status"] == "online" else "❌"
        
        html += f"""
                <div class="ship-card">
                    <div class="ship-name">{crew_member}</div>
                    <div class="ship-role">{info['role']}</div>
                    
                    <div class="ship-info">
                        <span class="ship-info-label">Ship:</span> {info['ship_name']}
                    </div>
                    <div class="ship-info">
                        <span class="ship-info-label">IP:</span> {info['ip']}
                    </div>
                    <div class="ship-info">
                        <span class="ship-info-label">Status:</span> 
                        <span class="{status_class}">{status_icon} {info['status'].upper()}</span>
                    </div>
                </div>
        """
    
    html += f"""
            </div>
            
            <div class="refresh-info">🔄 Auto-refreshing every 5 seconds</div>
            <div class="timestamp">Last updated: {status['timestamp']}</div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route("/api/status")
def api_status():
    """API endpoint for status"""
    return jsonify(manager.get_all_status())

if __name__ == "__main__":
    print("\n🌐 CREW STATUS DASHBOARD")
    print("=" * 70)
    print("Dashboard available at: http://localhost:6000")
    print("API endpoint: http://localhost:6000/api/status")
    print("\nRefresh rate: 5 seconds")
    print("Press Ctrl+C to stop")
    print("=" * 70 + "\n")
    
    try:
        app.run(host="127.0.0.1", port=6000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped.")
