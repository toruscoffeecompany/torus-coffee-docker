#!/usr/bin/env python3
"""
TOOL AC: Incident Response Playbooks
When the fleet breaks, crew follows these step-by-step playbooks
"""

import json
from datetime import datetime
from pathlib import Path

class IncidentPlaybooks:
    def __init__(self):
        self.playbooks_dir = Path("/data/incident_playbooks")
        self.playbooks_dir.mkdir(exist_ok=True)
    
    def create_playbook(self, incident_type, severity, steps, resolution_time):
        """Create an incident response playbook"""
        playbook = {
            "incident_type": incident_type,
            "severity": severity,
            "created": datetime.utcnow().isoformat(),
            "steps": steps,
            "estimated_resolution_time": resolution_time
        }
        return playbook
    
    def playbook_container_crash(self):
        """What to do when a container crashes"""
        return self.create_playbook(
            "Container Crash",
            "critical",
            [
                {
                    "step": 1,
                    "action": "Identify crashed container",
                    "command": "docker ps -a --filter status=exited",
                    "expected": "See list of exited containers"
                },
                {
                    "step": 2,
                    "action": "Get logs to find root cause",
                    "command": "docker logs <container_name>",
                    "expected": "See error messages in logs"
                },
                {
                    "step": 3,
                    "action": "Check resource limits",
                    "command": "docker inspect <container_name> | grep -A 10 Memory",
                    "expected": "Verify memory/CPU were not exceeded"
                },
                {
                    "step": 4,
                    "action": "Restart container",
                    "command": "docker restart <container_name>",
                    "expected": "Container starts successfully"
                },
                {
                    "step": 5,
                    "action": "Verify logs",
                    "command": "docker logs <container_name>",
                    "expected": "No error messages"
                },
                {
                    "step": 6,
                    "action": "Monitor for 5 minutes",
                    "command": "docker logs -f <container_name>",
                    "expected": "Container stays running"
                }
            ],
            "5-10 minutes"
        )
    
    def playbook_high_memory(self):
        """What to do when memory usage is critical"""
        return self.create_playbook(
            "High Memory Usage",
            "warning",
            [
                {
                    "step": 1,
                    "action": "Check memory usage",
                    "command": "docker stats --no-stream",
                    "expected": "See which container uses most memory"
                },
                {
                    "step": 2,
                    "action": "Check memory limit",
                    "command": "docker inspect <container_name> | grep Memory",
                    "expected": "See current limit vs actual usage"
                },
                {
                    "step": 3,
                    "action": "Is it a memory leak?",
                    "command": "watch -n 1 'docker inspect <container_name> | grep Memory'",
                    "expected": "Monitor for 60 seconds - is it growing?"
                },
                {
                    "step": 4,
                    "action": "If memory leak detected, restart",
                    "command": "docker restart <container_name>",
                    "expected": "Memory resets"
                },
                {
                    "step": 5,
                    "action": "If legitimate high usage, increase limit",
                    "command": "docker update -m 4g <container_name>",
                    "expected": "Container continues running without OOMKill"
                }
            ],
            "10-15 minutes"
        )
    
    def playbook_network_latency(self):
        """What to do when network is slow"""
        return self.create_playbook(
            "Network Latency",
            "warning",
            [
                {
                    "step": 1,
                    "action": "Check inter-ship latency",
                    "command": "ping -c 5 <ship_ip>",
                    "expected": "< 50ms latency"
                },
                {
                    "step": 2,
                    "action": "Check packet loss",
                    "command": "ping -c 100 <ship_ip> | grep loss",
                    "expected": "0% packet loss"
                },
                {
                    "step": 3,
                    "action": "Check network congestion",
                    "command": "docker stats --no-stream | grep -E 'CONTAINER|NET I/O'",
                    "expected": "See which container is using most bandwidth"
                },
                {
                    "step": 4,
                    "action": "Check Tailscale status",
                    "command": "tailscale status",
                    "expected": "All peers connected and active"
                },
                {
                    "step": 5,
                    "action": "If Tailscale offline, reconnect",
                    "command": "sudo systemctl restart tailscaled",
                    "expected": "Network restored"
                }
            ],
            "5-15 minutes"
        )
    
    def playbook_disk_full(self):
        """What to do when disk is full"""
        return self.create_playbook(
            "Disk Full",
            "critical",
            [
                {
                    "step": 1,
                    "action": "Check disk usage",
                    "command": "df -h /",
                    "expected": "See which filesystem is full (>90%)"
                },
                {
                    "step": 2,
                    "action": "Find large directories",
                    "command": "du -sh /* | sort -rh | head -10",
                    "expected": "See what's taking up space"
                },
                {
                    "step": 3,
                    "action": "Check Docker storage",
                    "command": "du -sh /var/lib/docker",
                    "expected": "See Docker volumes/images size"
                },
                {
                    "step": 4,
                    "action": "Clean up old containers",
                    "command": "docker container prune -f",
                    "expected": "Removes stopped containers"
                },
                {
                    "step": 5,
                    "action": "Clean up old images",
                    "command": "docker image prune -a --force",
                    "expected": "Removes unused images"
                },
                {
                    "step": 6,
                    "action": "Clean up everything unused",
                    "command": "docker system prune --volumes -f",
                    "expected": "Maximum disk space freed"
                }
            ],
            "10-20 minutes"
        )
    
    def playbook_no_connectivity(self):
        """What to do when can't reach a ship"""
        return self.create_playbook(
            "No Ship Connectivity",
            "critical",
            [
                {
                    "step": 1,
                    "action": "Verify network is up",
                    "command": "ping -c 5 8.8.8.8",
                    "expected": "Get responses"
                },
                {
                    "step": 2,
                    "action": "Check Tailscale connectivity",
                    "command": "tailscale status",
                    "expected": "See all ships in status"
                },
                {
                    "step": 3,
                    "action": "Try to ping the ship directly",
                    "command": "ping -c 5 <ship_tailscale_ip>",
                    "expected": "Get responses from ship"
                },
                {
                    "step": 4,
                    "action": "Check firewall rules",
                    "command": "sudo ufw status | grep 2375",
                    "expected": "Port 2375 should be allowed for Docker"
                },
                {
                    "step": 5,
                    "action": "If ship is completely offline, restart it",
                    "command": "Power cycle the physical machine",
                    "expected": "Ship comes back online"
                }
            ],
            "15-30 minutes"
        )
    
    def generate_all_playbooks(self):
        """Generate all incident playbooks"""
        playbooks = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_playbooks": 5,
            "playbooks": [
                self.playbook_container_crash(),
                self.playbook_high_memory(),
                self.playbook_network_latency(),
                self.playbook_disk_full(),
                self.playbook_no_connectivity()
            ]
        }
        
        # Save to file
        playbook_file = self.playbooks_dir / "ALL_INCIDENT_PLAYBOOKS.json"
        with open(playbook_file, 'w') as f:
            json.dump(playbooks, f, indent=2)
        
        print("\n📖 INCIDENT RESPONSE PLAYBOOKS")
        print("=" * 70)
        
        for playbook in playbooks["playbooks"]:
            severity_icon = "🚨" if playbook["severity"] == "critical" else "⚠️"
            print(f"\n{severity_icon} {playbook['incident_type']} (Severity: {playbook['severity'].upper()})")
            print(f"   Estimated time: {playbook['estimated_resolution_time']}")
            print(f"   Steps: {len(playbook['steps'])}")
            for step in playbook["steps"][:3]:  # Show first 3 steps
                print(f"   {step['step']}. {step['action']}")
            if len(playbook["steps"]) > 3:
                print(f"   ... and {len(playbook['steps']) - 3} more steps")
        
        print(f"\n✅ Full playbooks saved to {playbook_file}")
        print("\nThese playbooks are designed for quick crew response when incidents occur.")
        
        return playbooks

if __name__ == "__main__":
    playbooks = IncidentPlaybooks()
    playbooks.generate_all_playbooks()
