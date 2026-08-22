#!/usr/bin/env python3
"""
TOOL AK: Crew Quick Command Reference
One-command interface for all common operations
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class CrewQuickReference:
    def __init__(self):
        self.inbox_dir = Path("./00_Inbox")
        self.commands = {
            # Verification commands
            "verify-network": ("TOOL_AF_NETWORK_VERIFIER.py", "Verify all ships connected"),
            "verify-security": ("TOOL_AG_OPSEC_SECURITY_AUDIT.py", "Check OPSEC security"),
            "verify-health": ("TOOL_AH_FLEET_HEALTH_DIAGNOSTICS.py", "Check fleet health"),
            "verify-integration": ("TOOL_AI_INTEGRATION_VERIFIER.py", "Verify service integration"),
            "verify-all": ("TOOL_AJ_MASTER_VERIFICATION.py", "Run ALL verifications"),
            
            # Monitoring commands
            "monitor-dashboard": ("TOOL_AE_CREW_STATUS_DASHBOARD.py", "Start fleet dashboard"),
            "monitor-baseline": ("TOOL_AD_BASELINE_RECORDER.py", "Record system baseline"),
            
            # Deployment commands
            "deploy-check": ("TOOL_Z_READINESS_REPORT.py", "Check deployment readiness"),
            "deploy-extract": ("TOOL_W_MARKDOWN_EXTRACTOR.py", "Extract tools from markdown"),
            "deploy-test": ("TOOL_AA_LOCAL_TEST_HARNESS.py", "Test tools locally"),
            "deploy-verify": ("TOOL_AB_DEPLOYMENT_VERIFIER.py", "Verify deployed tools"),
            
            # Response commands
            "response-playbooks": ("TOOL_AC_INCIDENT_PLAYBOOKS.py", "Show incident playbooks"),
            
            # System commands
            "docker-monitor": ("TOOL_V_DOCKER_DESKTOP_MONITOR.py", "Monitor local Docker"),
            "broadcast": ("TOOL_X_CREW_BROADCASTER.py", "Broadcast to crew"),
            "validate": ("TOOL_Y_ARTIFACT_VALIDATOR.py", "Validate artifacts"),
        }
    
    def show_help(self):
        """Show help menu"""
        help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   🏴‍☠️ PIRATE FLEET QUICK COMMAND REFERENCE               ║
╚════════════════════════════════════════════════════════════════════════════╝

VERIFICATION COMMANDS:
  crew verify-network      → Check all ships connected (ping + Docker API)
  crew verify-security     → Run OPSEC security audit
  crew verify-health       → Check fleet health (disk, memory, CPU)
  crew verify-integration  → Test service integration
  crew verify-all          → Run ALL verification tests

MONITORING COMMANDS:
  crew monitor-dashboard   → Start fleet status dashboard (http://localhost:6000)
  crew monitor-baseline    → Record current system baseline

DEPLOYMENT COMMANDS:
  crew deploy-check        → Check if ready to deploy
  crew deploy-extract      → Extract 21 tools from markdown
  crew deploy-test         → Test tools locally before deployment
  crew deploy-verify       → Verify tools deployed on PINKCADY

INCIDENT RESPONSE:
  crew response-playbooks  → Show step-by-step incident playbooks

UTILITIES:
  crew docker-monitor      → Monitor local Docker Desktop
  crew broadcast           → Send message to crew
  crew validate            → Validate artifact files

USAGE EXAMPLES:

  Captain wants to see fleet status:
    $ crew monitor-dashboard
    Then open: http://localhost:6000

  Miss Pink before deploying:
    $ crew verify-all       (run all verifications)
    $ crew deploy-extract   (extract tools)
    $ crew deploy-test      (test locally)
    $ crew deploy-verify    (verify on PINKCADY)

  Sir Green when something breaks:
    $ crew response-playbooks    (get incident steps)

  Any crew member verifying connectivity:
    $ crew verify-network

OPTIONS:
  crew help                → Show this help
  crew list                → List all available commands
  crew status              → Show quick status of all ships

════════════════════════════════════════════════════════════════════════════════
"""
        print(help_text)
    
    def show_list(self):
        """List all commands"""
        print("\n🏴‍☠️ AVAILABLE COMMANDS:\n")
        
        current_section = None
        sections = {
            "VERIFICATION": ["verify-network", "verify-security", "verify-health", "verify-integration", "verify-all"],
            "MONITORING": ["monitor-dashboard", "monitor-baseline"],
            "DEPLOYMENT": ["deploy-check", "deploy-extract", "deploy-test", "deploy-verify"],
            "INCIDENT RESPONSE": ["response-playbooks"],
            "UTILITIES": ["docker-monitor", "broadcast", "validate"]
        }
        
        for section, commands in sections.items():
            print(f"\n📋 {section}:")
            for cmd in commands:
                if cmd in self.commands:
                    tool, desc = self.commands[cmd]
                    print(f"  crew {cmd:<20} → {desc}")
    
    def show_status(self):
        """Show quick status of all ships"""
        print("\n🚀 QUICK STATUS CHECK")
        print("=" * 70)
        print("\nRunning network connectivity check...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.inbox_dir / "TOOL_AF_NETWORK_VERIFIER.py")],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Extract status from output
            if "OPERATIONAL" in result.stdout:
                print("✅ FLEET STATUS: OPERATIONAL")
            elif "DEGRADED" in result.stdout:
                print("⚠️  FLEET STATUS: DEGRADED")
            else:
                print("❌ FLEET STATUS: OFFLINE")
            
            # Show last few lines
            lines = result.stdout.split("\n")
            for line in lines[-10:]:
                if line.strip():
                    print(line)
        
        except Exception as e:
            print(f"Error running status check: {e}")
    
    def run_command(self, command):
        """Run a crew command"""
        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            print("Run 'crew help' for available commands")
            return
        
        tool_name, description = self.commands[command]
        tool_path = self.inbox_dir / tool_name
        
        if not tool_path.exists():
            print(f"❌ Tool not found: {tool_path}")
            return
        
        print(f"\n▶️  Running: {description}")
        print("=" * 70)
        
        try:
            subprocess.run(
                [sys.executable, str(tool_path)],
                timeout=300  # 5 minute timeout
            )
        except subprocess.TimeoutExpired:
            print(f"\n⏱️  Command timed out after 5 minutes")
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Command stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    crew = CrewQuickReference()
    
    if len(sys.argv) < 2:
        crew.show_help()
        return
    
    command = sys.argv[1]
    
    if command == "help":
        crew.show_help()
    elif command == "list":
        crew.show_list()
    elif command == "status":
        crew.show_status()
    else:
        crew.run_command(command)

if __name__ == "__main__":
    main()
