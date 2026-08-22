#!/usr/bin/env python3
"""
TOOL AL: Automated Incident Context Capture
When something breaks, automatically capture the FULL state of the fleet at that moment
So debugging isn't "what happened?" but "here's exactly what the system looked like"
"""

import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

class IncidentContextCapture:
    def __init__(self):
        self.ships = {
            "SQUIDSTATION": {"ip": "100.83.247.14", "docker_port": 2375},
            "PINKCADY": {"ip": "100.106.235.103", "docker_port": 2375},
            "STEALTHATTACK": {"ip": "100.110.238.68", "docker_port": 2375}
        }
        self.incident_dir = Path("/data/incident_contexts")
        self.incident_dir.mkdir(exist_ok=True)
    
    def capture_full_context(self, incident_name=None):
        """Capture EVERYTHING at this moment"""
        if not incident_name:
            incident_name = f"incident_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        context = {
            "incident_name": incident_name,
            "captured_at": datetime.utcnow().isoformat(),
            "fleet_state": {},
            "per_ship_details": {}
        }
        
        print(f"\n🚨 CAPTURING INCIDENT CONTEXT: {incident_name}")
        print("=" * 80)
        
        for ship_name, ship_info in self.ships.items():
            print(f"\n📍 {ship_name}...")
            
            ship_context = {
                "timestamp": datetime.utcnow().isoformat(),
                "basics": {},
                "containers": {},
                "processes": {},
                "network": {},
                "logs": {}
            }
            
            try:
                # GET BASICS
                info_resp = requests.get(
                    f"http://{ship_info['ip']}:{ship_info['docker_port']}/v1.40/info",
                    timeout=5
                )
                if info_resp.status_code == 200:
                    info = info_resp.json()
                    ship_context["basics"] = {
                        "docker_version": info.get("ServerVersion"),
                        "containers_running": info.get("ContainersRunning"),
                        "containers_paused": info.get("ContainersPaused"),
                        "containers_stopped": info.get("Containers") - info.get("ContainersRunning", 0),
                        "images": info.get("Images"),
                        "memory_gb": round(info.get("MemTotal", 0) / 1024 / 1024 / 1024, 2),
                        "cpus": info.get("NCPU")
                    }
                    print(f"  ✅ Basics captured")
                
                # GET ALL CONTAINERS & THEIR STATE
                containers_resp = requests.get(
                    f"http://{ship_info['ip']}:{ship_info['docker_port']}/v1.40/containers/json?all=true",
                    timeout=5
                )
                if containers_resp.status_code == 200:
                    containers = containers_resp.json()
                    for container in containers:
                        container_id = container["Id"][:12]
                        
                        # Get full container details
                        inspect_resp = requests.get(
                            f"http://{ship_info['ip']}:{ship_info['docker_port']}/v1.40/containers/{container_id}/json",
                            timeout=5
                        )
                        
                        if inspect_resp.status_code == 200:
                            details = inspect_resp.json()
                            ship_context["containers"][container["Names"][0]] = {
                                "id": container_id,
                                "status": container["State"],
                                "image": container["Image"],
                                "created": container.get("Created"),
                                "state_detail": details.get("State", {}),
                                "restart_policy": details.get("HostConfig", {}).get("RestartPolicy"),
                                "memory_limit": details.get("HostConfig", {}).get("Memory"),
                                "cpu_limit": details.get("HostConfig", {}).get("CpuQuota"),
                                "labels": details.get("Config", {}).get("Labels", {}),
                                "env_vars": [e for e in details.get("Config", {}).get("Env", []) if not any(x in e for x in ["PASSWORD", "TOKEN", "SECRET", "KEY"])]  # No secrets
                            }
                    
                    print(f"  ✅ {len(containers)} containers captured")
                
                # GET LOGS FROM CONTAINERS
                for container in containers[:3]:  # Last 3 containers
                    container_id = container["Id"][:12]
                    try:
                        logs_resp = requests.get(
                            f"http://{ship_info['ip']}:{ship_info['docker_port']}/v1.40/containers/{container_id}/logs?stdout=true&stderr=true&tail=20",
                            timeout=5
                        )
                        if logs_resp.status_code == 200:
                            ship_context["logs"][container["Names"][0]] = logs_resp.text[:500]
                    except:
                        pass
                
                print(f"  ✅ Logs captured")
                
                # GET NETWORK INFO
                networks_resp = requests.get(
                    f"http://{ship_info['ip']}:{ship_info['docker_port']}/v1.40/networks",
                    timeout=5
                )
                if networks_resp.status_code == 200:
                    networks = networks_resp.json()
                    ship_context["network"]["networks_count"] = len(networks)
                    ship_context["network"]["networks"] = [n["Name"] for n in networks]
                
                print(f"  ✅ Network info captured")
                
            except Exception as e:
                ship_context["error"] = str(e)
                print(f"  ⚠️  Error: {str(e)[:50]}")
            
            context["per_ship_details"][ship_name] = ship_context
        
        # SAVE CONTEXT
        context_file = self.incident_dir / f"{incident_name}.json"
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)
        
        print(f"\n✅ Context saved to {context_file}")
        print(f"\n📊 Context includes:")
        print(f"  • Docker version on each ship")
        print(f"  • ALL containers (running + stopped)")
        print(f"  • Container details (resources, restart policy, labels)")
        print(f"  • Container logs (last 20 lines)")
        print(f"  • Network configuration")
        print(f"  • Memory/CPU info")
        
        return context

if __name__ == "__main__":
    import sys
    capture = IncidentContextCapture()
    incident_name = sys.argv[1] if len(sys.argv) > 1 else None
    capture.capture_full_context(incident_name)
