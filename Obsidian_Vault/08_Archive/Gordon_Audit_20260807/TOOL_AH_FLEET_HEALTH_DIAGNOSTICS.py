#!/usr/bin/env python3
"""
TOOL AH: Comprehensive Fleet Health Diagnostics
Deep health check: Docker daemon, disk space, memory, CPU, network, container health
"""

import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime

class FleetHealthDiagnostics:
    def __init__(self):
        self.ships = {
            "SQUIDSTATION": {"ip": "100.83.247.14", "docker_port": 2375},
            "PINKCADY": {"ip": "100.106.235.103", "docker_port": 2375},
            "STEALTHATTACK": {"ip": "100.110.238.68", "docker_port": 2375}
        }
        self.diagnostics_log = Path("/data/fleet_health_diagnostics.json")
        self.diagnostics_log.parent.mkdir(exist_ok=True)
    
    def get_ship_health(self, ship_name, ip, docker_port):
        """Get comprehensive health for one ship"""
        health = {
            "ship": ship_name,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unknown",
            "checks": {}
        }
        
        try:
            # Docker daemon health
            print(f"  {ship_name}: Checking Docker daemon...", end=" ", flush=True)
            info_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/info",
                timeout=5
            )
            
            if info_resp.status_code == 200:
                info = info_resp.json()
                health["checks"]["docker_daemon"] = {
                    "status": "healthy",
                    "version": info.get("ServerVersion", "unknown"),
                    "api_version": info.get("APIVersion", "unknown")
                }
                print("✅")
            else:
                health["checks"]["docker_daemon"] = {"status": "unhealthy", "code": info_resp.status_code}
                print("❌")
                return health
            
            # Disk space
            print(f"  {ship_name}: Checking disk usage...", end=" ", flush=True)
            health["checks"]["disk"] = {
                "status": "ok",
                "total_gb": round(info.get("DockerRootDir", "/var/lib/docker")),
                "available_gb": 0
            }
            
            # Try to get actual disk info
            try:
                stats_resp = requests.get(
                    f"http://{ip}:{docker_port}/v1.40/system/df",
                    timeout=5
                )
                if stats_resp.status_code == 200:
                    df = stats_resp.json()
                    images_size = sum(img.get("Size", 0) for img in df.get("Images", []))
                    containers_size = sum(c.get("SizeRw", 0) for c in df.get("Containers", []))
                    
                    health["checks"]["disk"]["images_gb"] = round(images_size / 1024 / 1024 / 1024, 2)
                    health["checks"]["disk"]["containers_gb"] = round(containers_size / 1024 / 1024 / 1024, 2)
                    
                    if images_size + containers_size > 50 * 1024 * 1024 * 1024:  # 50GB threshold
                        health["checks"]["disk"]["status"] = "warning"
            except:
                pass
            
            print("✅")
            
            # Memory
            print(f"  {ship_name}: Checking memory...", end=" ", flush=True)
            memory_gb = round(info.get("MemTotal", 0) / 1024 / 1024 / 1024, 2)
            health["checks"]["memory"] = {
                "total_gb": memory_gb,
                "status": "ok" if memory_gb >= 4 else "warning"
            }
            print("✅")
            
            # CPU
            print(f"  {ship_name}: Checking CPU...", end=" ", flush=True)
            cpu_count = info.get("NCPU", 0)
            health["checks"]["cpu"] = {
                "cores": cpu_count,
                "status": "ok" if cpu_count >= 2 else "warning"
            }
            print("✅")
            
            # Container health
            print(f"  {ship_name}: Checking containers...", end=" ", flush=True)
            containers_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/containers/json?all=true",
                timeout=5
            )
            
            if containers_resp.status_code == 200:
                containers = containers_resp.json()
                running = sum(1 for c in containers if "running" in c["Status"].lower())
                exited = sum(1 for c in containers if "exited" in c["Status"].lower())
                
                health["checks"]["containers"] = {
                    "total": len(containers),
                    "running": running,
                    "exited": exited,
                    "status": "ok" if exited == 0 or running >= exited else "warning"
                }
            print("✅")
            
            # Image count
            print(f"  {ship_name}: Checking images...", end=" ", flush=True)
            images_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/images/json",
                timeout=5
            )
            
            if images_resp.status_code == 200:
                images = images_resp.json()
                dangling = sum(1 for img in images if "<none>" in str(img.get("RepoTags", [])))
                
                health["checks"]["images"] = {
                    "total": len(images),
                    "dangling": dangling,
                    "status": "warning" if dangling > 10 else "ok"
                }
            print("✅")
            
            # Network
            print(f"  {ship_name}: Checking networks...", end=" ", flush=True)
            networks_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/networks",
                timeout=5
            )
            
            if networks_resp.status_code == 200:
                networks = networks_resp.json()
                health["checks"]["networks"] = {
                    "total": len(networks),
                    "status": "ok"
                }
            print("✅")
            
            # Overall status
            all_ok = all(
                c.get("status", "unknown") in ["ok", "healthy"]
                for c in health["checks"].values()
            )
            health["status"] = "healthy" if all_ok else "degraded"
        
        except Exception as e:
            health["status"] = "unreachable"
            health["error"] = str(e)
            print(f"❌ ({str(e)[:50]})")
        
        return health
    
    def run_full_diagnostics(self):
        """Run full fleet diagnostics"""
        print("\n🏥 FLEET HEALTH DIAGNOSTICS")
        print("=" * 80)
        
        diagnostics = {
            "timestamp": datetime.utcnow().isoformat(),
            "ships": [],
            "summary": {
                "healthy": 0,
                "degraded": 0,
                "unreachable": 0
            }
        }
        
        for ship_name, ship_info in self.ships.items():
            print(f"\n📍 {ship_name}:")
            
            health = self.get_ship_health(ship_name, ship_info["ip"], ship_info["docker_port"])
            diagnostics["ships"].append(health)
            
            # Update summary
            if health["status"] == "healthy":
                diagnostics["summary"]["healthy"] += 1
            elif health["status"] == "degraded":
                diagnostics["summary"]["degraded"] += 1
            else:
                diagnostics["summary"]["unreachable"] += 1
            
            # Print status details
            print(f"\n  Status: {health['status'].upper()}")
            
            for check_name, check_result in health.get("checks", {}).items():
                status_icon = "✅" if check_result.get("status") in ["ok", "healthy"] else "⚠️"
                
                if check_name == "docker_daemon":
                    print(f"  {status_icon} Docker: {check_result.get('version', 'unknown')}")
                elif check_name == "memory":
                    print(f"  {status_icon} Memory: {check_result.get('total_gb', 0)}GB")
                elif check_name == "cpu":
                    print(f"  {status_icon} CPU: {check_result.get('cores', 0)} cores")
                elif check_name == "disk":
                    size_info = f"Images: {check_result.get('images_gb', 0)}GB, Containers: {check_result.get('containers_gb', 0)}GB"
                    print(f"  {status_icon} Disk: {size_info}")
                elif check_name == "containers":
                    info = f"Total: {check_result.get('total', 0)}, Running: {check_result.get('running', 0)}, Exited: {check_result.get('exited', 0)}"
                    print(f"  {status_icon} Containers: {info}")
                elif check_name == "images":
                    info = f"Total: {check_result.get('total', 0)}, Dangling: {check_result.get('dangling', 0)}"
                    print(f"  {status_icon} Images: {info}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FLEET SUMMARY")
        print("=" * 80)
        print(f"✅ Healthy: {diagnostics['summary']['healthy']}/3")
        print(f"⚠️  Degraded: {diagnostics['summary']['degraded']}/3")
        print(f"❌ Unreachable: {diagnostics['summary']['unreachable']}/3")
        
        if diagnostics['summary']['healthy'] == 3:
            print(f"\n🚀 FLEET STATUS: FULLY OPERATIONAL")
        elif diagnostics['summary']['healthy'] >= 2:
            print(f"\n⚠️  FLEET STATUS: OPERATIONAL (DEGRADED)")
        else:
            print(f"\n❌ FLEET STATUS: CRITICAL")
        
        # Save
        with open(self.diagnostics_log, 'w') as f:
            json.dump(diagnostics, f, indent=2)
        
        print(f"\n📋 Diagnostics saved to {self.diagnostics_log}")
        
        return diagnostics

if __name__ == "__main__":
    diagnostics = FleetHealthDiagnostics()
    diagnostics.run_full_diagnostics()
