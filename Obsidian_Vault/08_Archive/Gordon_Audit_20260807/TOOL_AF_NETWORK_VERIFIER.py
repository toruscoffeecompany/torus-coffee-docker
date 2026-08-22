#!/usr/bin/env python3
"""
TOOL AF: End-to-End Network Connectivity Verification
Comprehensive check: verify all 3 ships connected, test Docker API, measure latency
"""

import subprocess
import requests
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class NetworkVerifier:
    def __init__(self):
        self.ships = {
            "Sir Green": {
                "name": "SQUIDSTATION",
                "local_ip": "192.168.0.39",
                "tailscale_ip": "100.83.247.14",
                "docker_port": 2375,
                "expected_services": ["docker", "kubernetes", "monitoring"]
            },
            "Miss Pink": {
                "name": "PINKCADY",
                "local_ip": "192.168.0.3",
                "tailscale_ip": "100.106.235.103",
                "docker_port": 2375,
                "expected_services": ["docker", "kubernetes", "webhook", "tools"]
            },
            "Sir Azure": {
                "name": "STEALTHATTACK",
                "local_ip": "192.168.0.10",
                "tailscale_ip": "100.110.238.68",
                "docker_port": 2375,
                "expected_services": ["docker", "gpu", "tailscale"]
            }
        }
        self.verify_log = Path("/data/network_verification.json")
        self.verify_log.parent.mkdir(exist_ok=True)
    
    def ping_host(self, ip, host_label):
        """Ping a host and measure latency"""
        try:
            result = subprocess.run(
                ["ping", "-c", "3", ip] if "linux" in subprocess.sys.platform else ["ping", "-n", "3", ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Extract latency
                if "avg" in result.stdout:  # Linux
                    avg = result.stdout.split("avg = ")[1].split("/")[0]
                    return {"host": host_label, "ip": ip, "reachable": True, "avg_latency_ms": float(avg)}
                elif "Average" in result.stdout:  # Windows
                    avg = result.stdout.split("Average = ")[1].split("ms")[0]
                    return {"host": host_label, "ip": ip, "reachable": True, "avg_latency_ms": float(avg)}
            
            return {"host": host_label, "ip": ip, "reachable": False, "error": "No response"}
        except Exception as e:
            return {"host": host_label, "ip": ip, "reachable": False, "error": str(e)}
    
    def test_docker_api(self, ip, port, ship_name):
        """Test Docker API connectivity"""
        try:
            response = requests.get(
                f"http://{ip}:{port}/v1.40/info",
                timeout=5
            )
            
            if response.status_code == 200:
                info = response.json()
                return {
                    "ship": ship_name,
                    "ip": ip,
                    "port": port,
                    "docker_accessible": True,
                    "docker_version": info.get("ServerVersion", "unknown"),
                    "containers_running": info.get("ContainersRunning", 0),
                    "containers_total": info.get("Containers", 0),
                    "images": info.get("Images", 0),
                    "memory_gb": round(info.get("MemTotal", 0) / 1024 / 1024 / 1024, 2)
                }
            else:
                return {
                    "ship": ship_name,
                    "ip": ip,
                    "docker_accessible": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "ship": ship_name,
                "ip": ip,
                "docker_accessible": False,
                "error": str(e)
            }
    
    def verify_all_connectivity(self):
        """Comprehensive network verification"""
        print("\n🔗 END-TO-END NETWORK CONNECTIVITY VERIFICATION")
        print("=" * 80)
        
        verification = {
            "timestamp": datetime.utcnow().isoformat(),
            "network_checks": {
                "ping_checks": [],
                "docker_api_checks": [],
                "cross_ship_connectivity": []
            },
            "summary": {}
        }
        
        # PHASE 1: Ping tests (both local and Tailscale IPs)
        print("\n📍 PHASE 1: PING CONNECTIVITY TEST")
        print("-" * 80)
        
        ping_results = []
        for crew_member, ship_info in self.ships.items():
            print(f"\n{crew_member} ({ship_info['name']}):")
            
            # Test local IP
            print(f"  Local IP ({ship_info['local_ip']})...", end=" ", flush=True)
            local_result = self.ping_host(ship_info['local_ip'], f"{ship_info['name']}-local")
            if local_result.get("reachable"):
                print(f"✅ ({local_result['avg_latency_ms']:.1f}ms)")
            else:
                print(f"❌ ({local_result.get('error')})")
            ping_results.append(local_result)
            
            # Test Tailscale IP
            print(f"  Tailscale IP ({ship_info['tailscale_ip']})...", end=" ", flush=True)
            tailscale_result = self.ping_host(ship_info['tailscale_ip'], f"{ship_info['name']}-tailscale")
            if tailscale_result.get("reachable"):
                print(f"✅ ({tailscale_result['avg_latency_ms']:.1f}ms)")
            else:
                print(f"❌ ({tailscale_result.get('error')})")
            ping_results.append(tailscale_result)
        
        verification["network_checks"]["ping_checks"] = ping_results
        reachable_count = sum(1 for r in ping_results if r.get("reachable"))
        print(f"\n✅ Reachable: {reachable_count}/{len(ping_results)} endpoints")
        
        # PHASE 2: Docker API tests
        print("\n🐋 PHASE 2: DOCKER API CONNECTIVITY TEST")
        print("-" * 80)
        
        docker_results = []
        for crew_member, ship_info in self.ships.items():
            print(f"\n{crew_member} ({ship_info['name']}):")
            print(f"  Docker API ({ship_info['tailscale_ip']}:{ship_info['docker_port']})...", end=" ", flush=True)
            
            docker_result = self.test_docker_api(
                ship_info['tailscale_ip'],
                ship_info['docker_port'],
                ship_info['name']
            )
            
            if docker_result.get("docker_accessible"):
                print(f"✅")
                print(f"    Version: {docker_result['docker_version']}")
                print(f"    Containers: {docker_result['containers_running']}/{docker_result['containers_total']} running")
                print(f"    Images: {docker_result['images']}")
                print(f"    Memory: {docker_result['memory_gb']} GB")
            else:
                print(f"❌ ({docker_result.get('error')})")
            
            docker_results.append(docker_result)
        
        verification["network_checks"]["docker_api_checks"] = docker_results
        accessible_count = sum(1 for r in docker_results if r.get("docker_accessible"))
        print(f"\n✅ Docker Accessible: {accessible_count}/{len(docker_results)} ships")
        
        # PHASE 3: Cross-ship connectivity
        print("\n🔀 PHASE 3: CROSS-SHIP CONNECTIVITY TEST")
        print("-" * 80)
        
        cross_ship = []
        for from_crew, from_info in self.ships.items():
            for to_crew, to_info in self.ships.items():
                if from_crew == to_crew:
                    continue
                
                print(f"\n{from_crew} → {to_crew}...", end=" ", flush=True)
                
                result = self.ping_host(
                    to_info['tailscale_ip'],
                    f"{from_crew}_to_{to_crew}"
                )
                
                if result.get("reachable"):
                    print(f"✅ ({result['avg_latency_ms']:.1f}ms)")
                else:
                    print(f"❌")
                
                cross_ship.append(result)
        
        verification["network_checks"]["cross_ship_connectivity"] = cross_ship
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 80)
        
        verification["summary"] = {
            "ping_reachable": reachable_count,
            "ping_total": len(ping_results),
            "docker_accessible": accessible_count,
            "docker_total": len(docker_results),
            "cross_ship_connected": sum(1 for c in cross_ship if c.get("reachable")),
            "cross_ship_total": len(cross_ship),
            "overall_status": "OPERATIONAL" if accessible_count == len(docker_results) else "DEGRADED"
        }
        
        print(f"\n✅ Ping Connectivity: {verification['summary']['ping_reachable']}/{verification['summary']['ping_total']}")
        print(f"✅ Docker Accessible: {verification['summary']['docker_accessible']}/{verification['summary']['docker_total']}")
        print(f"✅ Cross-Ship Links: {verification['summary']['cross_ship_connected']}/{verification['summary']['cross_ship_total']}")
        print(f"\n🚀 FLEET STATUS: {verification['summary']['overall_status']}")
        
        # Save
        with open(self.verify_log, 'w') as f:
            json.dump(verification, f, indent=2)
        
        print(f"\n📋 Verification saved to {self.verify_log}")
        
        return verification

if __name__ == "__main__":
    verifier = NetworkVerifier()
    verifier.verify_all_connectivity()
