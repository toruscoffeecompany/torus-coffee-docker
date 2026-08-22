#!/usr/bin/env python3
"""
TOOL AB: Deployment Verification
Post-deployment check: are all 21 tools running on PINKCADY?
"""

import requests
import json
from datetime import datetime
from pathlib import Path

class DeploymentVerifier:
    def __init__(self, pinkcady_ip="100.106.235.103", base_port=9000):
        self.pinkcady_ip = pinkcady_ip
        self.base_port = base_port
        self.verify_log = Path("/data/deployment_verification.json")
        self.verify_log.parent.mkdir(exist_ok=True)
    
    def check_tool_availability(self, tool_name, port):
        """Check if a deployed tool is accessible"""
        url = f"http://{self.pinkcady_ip}:{port}"
        
        try:
            response = requests.get(url, timeout=3)
            return {
                "tool": tool_name,
                "port": port,
                "accessible": response.status_code < 500,
                "status_code": response.status_code,
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
            }
        except requests.exceptions.ConnectionError:
            return {
                "tool": tool_name,
                "port": port,
                "accessible": False,
                "error": "Connection refused"
            }
        except requests.exceptions.Timeout:
            return {
                "tool": tool_name,
                "port": port,
                "accessible": False,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "port": port,
                "accessible": False,
                "error": str(e)
            }
    
    def verify_all_deployments(self):
        """Verify all 21 tools are running"""
        print("\n✔️  DEPLOYMENT VERIFICATION")
        print("=" * 70)
        print(f"Target: PINKCADY ({self.pinkcady_ip})")
        print(f"Checking ports {self.base_port}-{self.base_port + 20}...\n")
        
        verification = {
            "timestamp": datetime.utcnow().isoformat(),
            "target": self.pinkcady_ip,
            "total_tools": 21,
            "accessible": 0,
            "inaccessible": 0,
            "tools": []
        }
        
        # Tools to verify (port = base + offset)
        tools_to_verify = [
            ("CLI Tool", 0),
            ("Dashboard", 5000),
            ("Auto-Healer", 1),
            ("Backup Verifier", 2),
            ("Capacity Planner", 3),
            ("Model Manager", 4),
            ("Performance Profiler", 5),
            ("Cost Analyzer", 6),
            ("Security Scanner", 7),
            ("Doc Generator", 8),
            ("Disaster Recovery", 9),
            ("Compliance Auditor", 10),
            ("Load Testing", 11),
            ("Log Aggregation", 12),
            ("Deployment Orchestrator", 13),
            ("Workload Balancer", 14),
            ("Config Manager", 15),
            ("Network Optimizer", 16),
            ("Distributed Tracer", 17),
            ("Secret Manager", 18),
            ("Fleet Backup", 19)
        ]
        
        for tool_name, offset in tools_to_verify:
            port = self.base_port + offset if offset != 5000 else 5000
            check = self.check_tool_availability(tool_name, port)
            verification["tools"].append(check)
            
            if check.get("accessible"):
                verification["accessible"] += 1
                print(f"✅ {tool_name}: RUNNING ({check.get('response_time_ms')}ms)")
            else:
                verification["inaccessible"] += 1
                error = check.get("error", "Unknown")
                print(f"❌ {tool_name}: OFFLINE ({error})")
        
        # Summary
        print("\n" + "=" * 70)
        print(f"✅ Running: {verification['accessible']}/{verification['total_tools']}")
        print(f"❌ Offline: {verification['inaccessible']}/{verification['total_tools']}")
        
        if verification['total_tools'] > 0:
            uptime_pct = (verification['accessible'] / verification['total_tools']) * 100
            print(f"Fleet uptime: {uptime_pct:.1f}%")
        
        verification["all_running"] = verification["inaccessible"] == 0
        verification["operational"] = verification["accessible"] >= 19  # 90% threshold
        
        print(f"\n🚀 All systems operational: {'✅ YES' if verification['all_running'] else '⚠️  PARTIAL'}")
        print(f"Operational threshold (90%): {'✅ PASS' if verification['operational'] else '❌ FAIL'}")
        
        # Save
        with open(self.verify_log, 'w') as f:
            json.dump(verification, f, indent=2)
        
        print(f"\n📋 Verification saved to {self.verify_log}")
        
        return verification

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    verifier.verify_all_deployments()
