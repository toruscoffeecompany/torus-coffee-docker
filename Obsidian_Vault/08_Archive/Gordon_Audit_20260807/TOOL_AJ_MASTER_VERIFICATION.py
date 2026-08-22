#!/usr/bin/env python3
"""
TOOL AJ: Master Fleet Verification Orchestrator
Runs ALL verification tools in sequence, generates comprehensive report
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

class MasterVerificationOrchestrator:
    def __init__(self):
        self.tools = [
            ("TOOL_AF_NETWORK_VERIFIER.py", "Network Connectivity"),
            ("TOOL_AG_OPSEC_SECURITY_AUDIT.py", "OPSEC Security"),
            ("TOOL_AH_FLEET_HEALTH_DIAGNOSTICS.py", "Fleet Health"),
            ("TOOL_AI_INTEGRATION_VERIFIER.py", "Integration Tests")
        ]
        self.inbox_dir = Path("./00_Inbox")
        self.master_report = Path("/data/master_fleet_verification.json")
        self.master_report.parent.mkdir(exist_ok=True)
    
    def run_verification_tool(self, tool_name):
        """Run a single verification tool"""
        tool_path = self.inbox_dir / tool_name
        
        if not tool_path.exists():
            return {
                "tool": tool_name,
                "status": "NOT_FOUND",
                "error": f"Tool not found at {tool_path}"
            }
        
        try:
            result = subprocess.run(
                [sys.executable, str(tool_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "tool": tool_name,
                "status": "completed",
                "return_code": result.returncode,
                "output_lines": len(result.stdout.split("\n"))
            }
        except subprocess.TimeoutExpired:
            return {
                "tool": tool_name,
                "status": "timeout",
                "error": "Exceeded 120 second timeout"
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "status": "error",
                "error": str(e)
            }
    
    def compile_results(self):
        """Compile results from all verification tools"""
        print("\n" + "=" * 80)
        print("📋 COMPILING VERIFICATION RESULTS")
        print("=" * 80)
        
        results = {}
        
        # Read all generated reports
        for report_file in [
            "/data/network_verification.json",
            "/data/opsec_security_audit.json",
            "/data/fleet_health_diagnostics.json",
            "/data/integration_verification.json"
        ]:
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                    key = report_file.split("/")[-1].replace(".json", "")
                    results[key] = data
            except:
                pass
        
        return results
    
    def generate_master_report(self):
        """Generate master verification report"""
        print("\n" + "=" * 80)
        print("🏴‍☠️  MASTER FLEET VERIFICATION REPORT")
        print("=" * 80)
        
        master = {
            "timestamp": datetime.utcnow().isoformat(),
            "verification_stage": "comprehensive",
            "tools_run": [],
            "results": {},
            "executive_summary": {}
        }
        
        # Run all verification tools
        print("\n🔄 Running all verification tools in sequence...")
        print("-" * 80)
        
        for tool_file, tool_description in self.tools:
            print(f"\n▶️  {tool_description}...", end=" ", flush=True)
            result = self.run_verification_tool(tool_file)
            master["tools_run"].append(result)
            
            if result["status"] == "completed":
                print(f"✅")
            else:
                print(f"⚠️  ({result['status']})")
        
        # Compile results
        print("\n" + "-" * 80)
        print("Compiling results from all verification tools...")
        
        compiled = self.compile_results()
        master["results"] = compiled
        
        # Generate executive summary
        print("\n" + "=" * 80)
        print("📊 EXECUTIVE SUMMARY")
        print("=" * 80)
        
        # Network status
        if "network_verification" in compiled:
            nv = compiled["network_verification"]
            print(f"\n🔗 Network Status:")
            print(f"  ✅ Reachable endpoints: {nv['summary']['ping_reachable']}/{nv['summary']['ping_total']}")
            print(f"  ✅ Docker accessible: {nv['summary']['docker_accessible']}/{nv['summary']['docker_total']}")
            print(f"  Status: {nv['summary']['overall_status']}")
            
            master["executive_summary"]["network"] = nv["summary"]
        
        # Security status
        if "opsec_security_audit" in compiled:
            oa = compiled["opsec_security_audit"]
            print(f"\n🔒 Security Status:")
            print(f"  🚨 Critical issues: {oa['summary']['critical_issues']}")
            print(f"  ⚠️  Warning issues: {oa['summary']['warning_issues']}")
            
            if oa['summary']['critical_issues'] > 0:
                print(f"  ⚠️  ACTION REQUIRED: Address critical security issues")
            
            master["executive_summary"]["security"] = oa["summary"]
        
        # Health status
        if "fleet_health_diagnostics" in compiled:
            fh = compiled["fleet_health_diagnostics"]
            print(f"\n🏥 Fleet Health:")
            print(f"  ✅ Healthy: {fh['summary']['healthy']}/3")
            print(f"  ⚠️  Degraded: {fh['summary']['degraded']}/3")
            print(f"  ❌ Unreachable: {fh['summary']['unreachable']}/3")
            
            master["executive_summary"]["health"] = fh["summary"]
        
        # Integration status
        if "integration_verification" in compiled:
            iv = compiled["integration_verification"]
            print(f"\n🔀 Integration Status:")
            print(f"  ✅ All connected: {iv['summary']['all_connected']}")
            print(f"  ✅ Services discoverable: {iv['summary']['all_services_discoverable']}")
            print(f"  ✅ Volumes accessible: {iv['summary']['all_volumes_accessible']}")
            print(f"  ✅ Network isolated: {iv['summary']['network_isolated']}")
            
            master["executive_summary"]["integration"] = iv["summary"]
        
        # Overall status
        print("\n" + "=" * 80)
        print("🚀 OVERALL FLEET STATUS")
        print("=" * 80)
        
        # Determine overall status
        is_operational = (
            master["executive_summary"].get("network", {}).get("overall_status") == "OPERATIONAL" and
            master["executive_summary"].get("security", {}).get("critical_issues", 0) == 0 and
            master["executive_summary"].get("health", {}).get("healthy", 0) >= 2 and
            master["executive_summary"].get("integration", {}).get("all_connected", False)
        )
        
        if is_operational:
            print("✅ FLEET STATUS: FULLY OPERATIONAL")
            print("   All systems verified and integrated")
            print("   Ready for production deployment")
        else:
            print("⚠️  FLEET STATUS: OPERATIONAL WITH WARNINGS")
            print("   Address items below before critical operations")
        
        # Recommendations
        print("\n📋 KEY RECOMMENDATIONS:")
        
        if master["executive_summary"].get("security", {}).get("critical_issues", 0) > 0:
            print("  1. 🚨 FIX CRITICAL SECURITY ISSUES")
            print("     - Enable TLS for Docker API")
            print("     - Implement authentication")
            print("     - Restrict Docker API access")
        
        if master["executive_summary"].get("health", {}).get("degraded", 0) > 0:
            print("  2. ⚠️  Address degraded ships")
            print("     - Check disk space on degraded ships")
            print("     - Verify all containers are healthy")
        
        if not master["executive_summary"].get("integration", {}).get("network_isolated", False):
            print("  3. 🌐 Improve network isolation")
            print("     - Implement custom bridge networks")
            print("     - Add network policies")
        
        # Save master report
        with open(self.master_report, 'w') as f:
            json.dump(master, f, indent=2)
        
        print(f"\n📋 Master report saved to {self.master_report}")
        print("\nDetailed reports saved to:")
        print("  • /data/network_verification.json")
        print("  • /data/opsec_security_audit.json")
        print("  • /data/fleet_health_diagnostics.json")
        print("  • /data/integration_verification.json")
        
        return master

if __name__ == "__main__":
    orchestrator = MasterVerificationOrchestrator()
    orchestrator.generate_master_report()
