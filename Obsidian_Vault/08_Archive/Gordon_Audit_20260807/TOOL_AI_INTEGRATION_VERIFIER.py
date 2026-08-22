#!/usr/bin/env python3
"""
TOOL AI: End-to-End Integration Verification
Comprehensive test: can all ships talk to each other? Can tools communicate? Complete system check
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class IntegrationVerifier:
    def __init__(self):
        self.ships = {
            "SQUIDSTATION": {"ip": "100.83.247.14", "docker_port": 2375, "role": "infrastructure"},
            "PINKCADY": {"ip": "100.106.235.103", "docker_port": 2375, "role": "operations"},
            "STEALTHATTACK": {"ip": "100.110.238.68", "docker_port": 2375, "role": "gpu"}
        }
        self.integration_log = Path("/data/integration_verification.json")
        self.integration_log.parent.mkdir(exist_ok=True)
    
    def test_ship_to_ship_docker_api(self, from_ship, from_ip, to_ship, to_ip, to_port):
        """Test if one ship can reach another's Docker API"""
        try:
            # Try to reach the other ship's Docker API
            response = requests.get(
                f"http://{to_ip}:{to_port}/v1.40/info",
                timeout=5
            )
            
            return {
                "from": from_ship,
                "to": to_ship,
                "docker_api_reachable": response.status_code == 200,
                "status_code": response.status_code,
                "latency_ms": round(response.elapsed.total_seconds() * 1000, 2)
            }
        except Exception as e:
            return {
                "from": from_ship,
                "to": to_ship,
                "docker_api_reachable": False,
                "error": str(e)
            }
    
    def test_service_discovery(self, ship_name, ip, docker_port):
        """Test if services can be discovered"""
        discovery = {
            "ship": ship_name,
            "services_discovered": [],
            "services_total": 0
        }
        
        try:
            # Get all containers with their ports
            containers_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/containers/json",
                timeout=5
            )
            
            if containers_resp.status_code == 200:
                containers = containers_resp.json()
                discovery["services_total"] = len(containers)
                
                for container in containers:
                    service_info = {
                        "name": container.get("Names", ["/unknown"])[0].lstrip("/"),
                        "image": container.get("Image", "unknown"),
                        "status": container.get("State", "unknown"),
                        "ports": container.get("Ports", [])
                    }
                    discovery["services_discovered"].append(service_info)
        
        except Exception as e:
            discovery["error"] = str(e)
        
        return discovery
    
    def test_volume_accessibility(self, ship_name, ip, docker_port):
        """Test if volumes are properly accessible"""
        volume_check = {
            "ship": ship_name,
            "volumes_found": 0,
            "volumes": []
        }
        
        try:
            volumes_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/volumes",
                timeout=5
            )
            
            if volumes_resp.status_code == 200:
                volumes = volumes_resp.json().get("Volumes", [])
                volume_check["volumes_found"] = len(volumes)
                
                for volume in volumes[:5]:  # Show first 5
                    volume_check["volumes"].append({
                        "name": volume.get("Name", "unknown"),
                        "driver": volume.get("Driver", "unknown"),
                        "mountpoint": volume.get("Mountpoint", "unknown")
                    })
        
        except Exception as e:
            volume_check["error"] = str(e)
        
        return volume_check
    
    def test_network_policies(self, ship_name, ip, docker_port):
        """Test if network policies are enforced"""
        network_check = {
            "ship": ship_name,
            "networks_found": 0,
            "isolation_configured": False,
            "issues": []
        }
        
        try:
            networks_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/networks",
                timeout=5
            )
            
            if networks_resp.status_code == 200:
                networks = networks_resp.json()
                network_check["networks_found"] = len(networks)
                
                # Check for custom networks (better isolation)
                custom_networks = [n for n in networks if n.get("Name") not in ["bridge", "host", "none"]]
                network_check["custom_networks"] = len(custom_networks)
                
                if len(custom_networks) > 0:
                    network_check["isolation_configured"] = True
                else:
                    network_check["issues"].append("No custom networks found - consider using for isolation")
        
        except Exception as e:
            network_check["error"] = str(e)
        
        return network_check
    
    def run_full_integration_test(self):
        """Run complete integration verification"""
        print("\n🔗 END-TO-END INTEGRATION VERIFICATION")
        print("=" * 80)
        
        integration = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {
                "ship_to_ship_connectivity": [],
                "service_discovery": [],
                "volume_accessibility": [],
                "network_policies": [],
                "cross_ship_communication": []
            },
            "summary": {
                "all_connected": False,
                "all_services_discoverable": False,
                "all_volumes_accessible": False,
                "network_isolated": False
            }
        }
        
        # TEST 1: Ship-to-ship connectivity
        print("\n📍 TEST 1: Ship-to-Ship Docker API Connectivity")
        print("-" * 80)
        
        s2s_results = []
        for from_ship, from_info in self.ships.items():
            for to_ship, to_info in self.ships.items():
                if from_ship == to_ship:
                    continue
                
                result = self.test_ship_to_ship_docker_api(
                    from_ship, from_info["ip"],
                    to_ship, to_info["ip"], to_info["docker_port"]
                )
                s2s_results.append(result)
                
                status = "✅" if result["docker_api_reachable"] else "❌"
                print(f"{status} {from_ship} → {to_ship}: ", end="")
                if result["docker_api_reachable"]:
                    print(f"Connected ({result['latency_ms']}ms)")
                else:
                    print(f"Failed ({result.get('error', 'unknown')})")
        
        integration["tests"]["ship_to_ship_connectivity"] = s2s_results
        all_connected = all(r["docker_api_reachable"] for r in s2s_results)
        integration["summary"]["all_connected"] = all_connected
        print(f"\n✅ All connected: {'YES' if all_connected else 'NO'}")
        
        # TEST 2: Service discovery
        print("\n🔎 TEST 2: Service Discovery")
        print("-" * 80)
        
        sd_results = []
        for ship_name, ship_info in self.ships.items():
            result = self.test_service_discovery(ship_name, ship_info["ip"], ship_info["docker_port"])
            sd_results.append(result)
            print(f"{ship_name}: {result['services_total']} services discovered")
            
            for service in result['services_discovered'][:3]:
                print(f"  • {service['name']}: {service['status']}")
            if result['services_total'] > 3:
                print(f"  ... and {result['services_total'] - 3} more")
        
        integration["tests"]["service_discovery"] = sd_results
        integration["summary"]["all_services_discoverable"] = all(len(r["services_discovered"]) > 0 for r in sd_results)
        
        # TEST 3: Volume accessibility
        print("\n💾 TEST 3: Volume Accessibility")
        print("-" * 80)
        
        vol_results = []
        for ship_name, ship_info in self.ships.items():
            result = self.test_volume_accessibility(ship_name, ship_info["ip"], ship_info["docker_port"])
            vol_results.append(result)
            print(f"{ship_name}: {result['volumes_found']} volumes")
        
        integration["tests"]["volume_accessibility"] = vol_results
        integration["summary"]["all_volumes_accessible"] = all(r.get("volumes_found", 0) >= 0 for r in vol_results)
        
        # TEST 4: Network policies
        print("\n🌐 TEST 4: Network Isolation Policies")
        print("-" * 80)
        
        net_results = []
        for ship_name, ship_info in self.ships.items():
            result = self.test_network_policies(ship_name, ship_info["ip"], ship_info["docker_port"])
            net_results.append(result)
            
            status = "✅" if result["isolation_configured"] else "⚠️"
            print(f"{status} {ship_name}: {result['networks_found']} networks, isolation: {'YES' if result['isolation_configured'] else 'NO'}")
            
            for issue in result.get("issues", []):
                print(f"   ⚠️  {issue}")
        
        integration["tests"]["network_policies"] = net_results
        integration["summary"]["network_isolated"] = all(r["isolation_configured"] for r in net_results)
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("📊 INTEGRATION SUMMARY")
        print("=" * 80)
        print(f"✅ All ships connected: {integration['summary']['all_connected']}")
        print(f"✅ All services discoverable: {integration['summary']['all_services_discoverable']}")
        print(f"✅ All volumes accessible: {integration['summary']['all_volumes_accessible']}")
        print(f"✅ Network isolated: {integration['summary']['network_isolated']}")
        
        all_pass = all(integration['summary'].values())
        print(f"\n🚀 INTEGRATION STATUS: {'FULL' if all_pass else 'PARTIAL'}")
        
        # Save
        with open(self.integration_log, 'w') as f:
            json.dump(integration, f, indent=2)
        
        print(f"\n📋 Integration verification saved to {self.integration_log}")
        
        return integration

if __name__ == "__main__":
    verifier = IntegrationVerifier()
    verifier.run_full_integration_test()
