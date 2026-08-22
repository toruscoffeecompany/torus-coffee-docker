#!/usr/bin/env python3
"""
TOOL AO: Automated Runbook Generator
Takes incident history and fleet state, generates EXECUTABLE runbooks
Crew doesn't read documentation - they execute commands
"""

import json
from pathlib import Path
from datetime import datetime

class AutomatedRunbookGenerator:
    def __init__(self):
        self.runbooks_dir = Path("/data/runbooks")
        self.runbooks_dir.mkdir(exist_ok=True)
    
    def generate_runbook(self, scenario_name, scenario_description, steps):
        """Generate executable runbook"""
        runbook = {
            "scenario": scenario_name,
            "description": scenario_description,
            "generated_at": datetime.utcnow().isoformat(),
            "estimated_time_minutes": len(steps) * 2,
            "steps": steps,
            "success_criteria": "All steps execute without errors"
        }
        return runbook
    
    def generate_high_memory_runbook(self):
        """When a ship runs out of memory"""
        return self.generate_runbook(
            scenario_name="High Memory Usage Response",
            scenario_description="Execute this when memory usage >85%",
            steps=[
                {
                    "step": 1,
                    "title": "Check current memory",
                    "command": "python TOOL_AH_FLEET_HEALTH_DIAGNOSTICS.py",
                    "expected_output": "Memory usage percentages for all ships"
                },
                {
                    "step": 2,
                    "title": "Identify offending container",
                    "command": "docker stats --no-stream | grep -E 'CONTAINER|NAME' | head -10",
                    "expected_output": "Top memory-using containers"
                },
                {
                    "step": 3,
                    "title": "Review container logs",
                    "command": "docker logs <container_name> | tail -50",
                    "expected_output": "Last 50 lines of container logs"
                },
                {
                    "step": 4,
                    "title": "Option A: Restart container",
                    "command": "docker restart <container_name>",
                    "expected_output": "Container restarted"
                },
                {
                    "step": 5,
                    "title": "Option B: Increase memory limit",
                    "command": "docker update -m 4g <container_name>",
                    "expected_output": "Memory limit updated"
                },
                {
                    "step": 6,
                    "title": "Verify resolution",
                    "command": "docker stats --no-stream <container_name>",
                    "expected_output": "Memory usage should be lower"
                }
            ]
        )
    
    def generate_network_issue_runbook(self):
        """When ships can't reach each other"""
        return self.generate_runbook(
            scenario_name="Network Connectivity Issue",
            scenario_description="Execute this when ships can't communicate",
            steps=[
                {
                    "step": 1,
                    "title": "Verify network connectivity",
                    "command": "python TOOL_AF_NETWORK_VERIFIER.py",
                    "expected_output": "Network connectivity report"
                },
                {
                    "step": 2,
                    "title": "Check Tailscale status",
                    "command": "tailscale status",
                    "expected_output": "All peers should be connected"
                },
                {
                    "step": 3,
                    "title": "If Tailscale offline, restart it",
                    "command": "sudo systemctl restart tailscaled",
                    "expected_output": "Service restarted"
                },
                {
                    "step": 4,
                    "title": "Reconnect to Tailscale",
                    "command": "tailscale login",
                    "expected_output": "Login successful"
                },
                {
                    "step": 5,
                    "title": "Verify connectivity again",
                    "command": "python TOOL_AF_NETWORK_VERIFIER.py",
                    "expected_output": "All ships now reachable"
                }
            ]
        )
    
    def generate_deployment_runbook(self):
        """Deploy all 21 tools"""
        return self.generate_runbook(
            scenario_name="Deploy Fleet Tools",
            scenario_description="Deploy all 21 operational tools to PINKCADY",
            steps=[
                {
                    "step": 1,
                    "title": "Verify deployment readiness",
                    "command": "python TOOL_Z_READINESS_REPORT.py",
                    "expected_output": "All artifacts ready"
                },
                {
                    "step": 2,
                    "title": "Verify network",
                    "command": "python TOOL_AF_NETWORK_VERIFIER.py",
                    "expected_output": "All ships connected"
                },
                {
                    "step": 3,
                    "title": "Extract tools from markdown",
                    "command": "python TOOL_W_MARKDOWN_EXTRACTOR.py",
                    "expected_output": "21 tools extracted to ./pirate_tools/"
                },
                {
                    "step": 4,
                    "title": "Test tools locally",
                    "command": "python TOOL_AA_LOCAL_TEST_HARNESS.py",
                    "expected_output": "All tools pass local tests"
                },
                {
                    "step": 5,
                    "title": "Deploy to PINKCADY",
                    "command": "bash /opt/pirate-fleet-tools/deploy_all_tools.sh",
                    "expected_output": "All 21 tools deployed"
                },
                {
                    "step": 6,
                    "title": "Verify deployment",
                    "command": "python TOOL_AB_DEPLOYMENT_VERIFIER.py",
                    "expected_output": "21/21 tools running on PINKCADY"
                }
            ]
        )
    
    def generate_disaster_recovery_runbook(self):
        """Recover from complete system failure"""
        return self.generate_runbook(
            scenario_name="Disaster Recovery",
            scenario_description="Execute if entire fleet is down",
            steps=[
                {
                    "step": 1,
                    "title": "Check if Docker daemon is running",
                    "command": "docker ps",
                    "expected_output": "Docker responds or error message"
                },
                {
                    "step": 2,
                    "title": "If Docker stopped, restart it",
                    "command": "sudo systemctl restart docker",
                    "expected_output": "Docker service restarted"
                },
                {
                    "step": 3,
                    "title": "Restore from latest backup",
                    "command": "python TOOL_AH_FLEET_HEALTH_DIAGNOSTICS.py",
                    "expected_output": "List backup locations"
                },
                {
                    "step": 4,
                    "title": "Verify backups exist",
                    "command": "ls -lh /backups/",
                    "expected_output": "Recent backup files"
                },
                {
                    "step": 5,
                    "title": "Restore from backup",
                    "command": "tar -xzf /backups/latest_backup.tar.gz -C /",
                    "expected_output": "Backup restored"
                },
                {
                    "step": 6,
                    "title": "Verify all systems online",
                    "command": "python TOOL_AJ_MASTER_VERIFICATION.py",
                    "expected_output": "Fleet operational"
                }
            ]
        )
    
    def generate_all_runbooks(self):
        """Generate all runbooks"""
        print("\n📖 GENERATING AUTOMATED RUNBOOKS")
        print("=" * 80)
        
        runbooks = [
            ("high_memory_response", self.generate_high_memory_runbook()),
            ("network_issue_response", self.generate_network_issue_runbook()),
            ("deploy_fleet_tools", self.generate_deployment_runbook()),
            ("disaster_recovery", self.generate_disaster_recovery_runbook())
        ]
        
        for runbook_name, runbook_content in runbooks:
            print(f"\n📋 {runbook_name}...", end=" ", flush=True)
            
            runbook_file = self.runbooks_dir / f"{runbook_name}.json"
            with open(runbook_file, 'w') as f:
                json.dump(runbook_content, f, indent=2)
            
            # Also generate as bash script
            bash_file = self.runbooks_dir / f"{runbook_name}.sh"
            with open(bash_file, 'w') as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"# {runbook_content['scenario']}\n")
                f.write(f"# {runbook_content['description']}\n\n")
                
                for step in runbook_content['steps']:
                    f.write(f"\n# Step {step['step']}: {step['title']}\n")
                    f.write(f"# Expected: {step['expected_output']}\n")
                    f.write(f"{step['command']}\n")
            
            print("✅")
        
        print(f"\n✅ Runbooks saved to {self.runbooks_dir}")
        print("\nGenerated runbooks:")
        for runbook_name, _ in runbooks:
            print(f"  • {runbook_name}.json (detailed)")
            print(f"  • {runbook_name}.sh (executable)")

if __name__ == "__main__":
    generator = AutomatedRunbookGenerator()
    generator.generate_all_runbooks()
