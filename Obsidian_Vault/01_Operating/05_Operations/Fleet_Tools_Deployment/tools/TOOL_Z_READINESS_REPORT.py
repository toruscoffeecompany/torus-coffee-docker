#!/usr/bin/env python3
"""
TOOL Z: Instant Deployment Readiness Report
Shows real-time status of all 21 tools and whether they're ready to deploy
"""

import os
import json
from pathlib import Path
from datetime import datetime

class ReadinessReport:
    def __init__(self, inbox_dir="./00_Inbox", tools_dir="./pirate_tools"):
        self.inbox_dir = Path(inbox_dir)
        self.tools_dir = Path(tools_dir)
        self.report_path = Path("/data/readiness_report.json")
        self.report_path.parent.mkdir(exist_ok=True)
    
    def check_markdown_artifacts(self):
        """Check if all markdown files exist"""
        artifacts = {
            "PIRATE_CREW_CLI_TOOL.md": "CLI tool + dashboard foundations",
            "FLEET_MONITORING_DASHBOARD.md": "Real-time fleet dashboard",
            "ALL_FIVE_TOOLS_COMPLETE.md": "Tools A-E (Backup, Capacity, Models, etc)",
            "FIVE_MORE_TOOLS_COMPLETE.md": "Tools F-J (Auto-Healer, Profiler, etc)",
            "TOOLS_K_THROUGH_O_COMPLETE.md": "Tools K-O (DR, Compliance, Load Test, etc)",
            "ADVANCED_CROSS_SHIP_TOOLS_P_TO_U.md": "Tools P-U (Workload Balancer, Config Mgr, etc)"
        }
        
        results = {}
        for artifact, description in artifacts.items():
            path = self.inbox_dir / artifact
            exists = path.exists()
            results[artifact] = {
                "exists": exists,
                "description": description,
                "size_kb": round(path.stat().st_size / 1024, 1) if exists else 0
            }
        
        return results
    
    def check_extracted_tools(self):
        """Check if tools have been extracted"""
        if not self.tools_dir.exists():
            return {"extracted": False, "count": 0, "tools": []}
        
        py_files = list(self.tools_dir.glob("*.py"))
        return {
            "extracted": len(py_files) > 0,
            "count": len(py_files),
            "tools": [f.name for f in sorted(py_files)]
        }
    
    def check_deployment_helpers(self):
        """Check if deployment helper files exist"""
        helpers = {
            "EXACT_DEPLOYMENT_PROMPT_FOR_MISS_PINK.md": "Step-by-step deployment guide",
            "GORDON_CAN_BUILD_RIGHT_NOW.md": "Tools V-Z documentation"
        }
        
        results = {}
        for helper, description in helpers.items():
            path = self.inbox_dir / helper
            results[helper] = {
                "exists": path.exists(),
                "description": description
            }
        
        return results
    
    def check_immediate_tools(self):
        """Check if immediate-use tools exist (V-Z)"""
        immediate = {
            "TOOL_V_DOCKER_DESKTOP_MONITOR.py": "Monitor local Docker Desktop",
            "TOOL_W_MARKDOWN_EXTRACTOR.py": "Extract tools from markdown",
            "TOOL_X_CREW_BROADCASTER.py": "Send status to crew",
            "TOOL_Y_ARTIFACT_VALIDATOR.py": "Validate Python syntax",
            "TOOL_Z_READINESS_REPORT.py": "This readiness report"
        }
        
        results = {}
        for tool, description in immediate.items():
            path = self.inbox_dir / tool
            results[tool] = {
                "exists": path.exists(),
                "description": description,
                "executable": os.access(path, os.X_OK) if path.exists() else False
            }
        
        return results
    
    def generate_full_report(self):
        """Generate complete readiness report"""
        artifacts = self.check_markdown_artifacts()
        extracted = self.check_extracted_tools()
        helpers = self.check_deployment_helpers()
        immediate = self.check_immediate_tools()
        
        # Count artifacts
        artifacts_found = sum(1 for v in artifacts.values() if v["exists"])
        artifacts_total = len(artifacts)
        
        # Count extracted
        extracted_count = extracted["count"]
        
        # Count helpers
        helpers_found = sum(1 for v in helpers.values() if v["exists"])
        
        # Count immediate tools
        immediate_found = sum(1 for v in immediate.values() if v["exists"])
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "READY FOR DEPLOYMENT" if artifacts_found == artifacts_total else "INCOMPLETE",
            "summary": {
                "markdown_artifacts": f"{artifacts_found}/{artifacts_total} found",
                "extracted_tools": f"{extracted_count} (from markdown)",
                "deployment_helpers": f"{helpers_found}/2 available",
                "immediate_tools": f"{immediate_found}/5 available"
            },
            "details": {
                "markdown_artifacts": artifacts,
                "extracted_tools": extracted,
                "deployment_helpers": helpers,
                "immediate_tools": immediate
            },
            "readiness_checklist": {
                "artifacts_available": artifacts_found == artifacts_total,
                "deployment_prompt_available": helpers["EXACT_DEPLOYMENT_PROMPT_FOR_MISS_PINK.md"]["exists"],
                "immediate_tools_available": immediate_found >= 5,
                "overall_ready": (artifacts_found == artifacts_total and 
                                helpers["EXACT_DEPLOYMENT_PROMPT_FOR_MISS_PINK.md"]["exists"])
            },
            "next_steps": [
                "1. Miss Pink: Run TOOL_W_MARKDOWN_EXTRACTOR.py to extract all 21 tools",
                "2. Run TOOL_Y_ARTIFACT_VALIDATOR.py to verify extraction",
                "3. Follow EXACT_DEPLOYMENT_PROMPT_FOR_MISS_PINK.md to deploy",
                "4. Or: Use immediate tools (V-Z) for quick status checks"
            ]
        }
        
        return report
    
    def print_report(self):
        """Pretty-print the readiness report"""
        report = self.generate_full_report()
        
        print("\n" + "=" * 70)
        print("🚀 PIRATE FLEET DEPLOYMENT READINESS REPORT")
        print("=" * 70)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Status: {report['status']}")
        print()
        
        print("📊 SUMMARY:")
        for key, value in report['summary'].items():
            print(f"  • {key}: {value}")
        
        print("\n✅ READINESS CHECKLIST:")
        for check, status in report['readiness_checklist'].items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {check}")
        
        print("\n📋 NEXT STEPS:")
        for step in report['next_steps']:
            print(f"  {step}")
        
        print("\n" + "=" * 70)
        
        # Save report
        with open(self.report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to {self.report_path}")
        
        return report

if __name__ == "__main__":
    readiness = ReadinessReport()
    readiness.print_report()
