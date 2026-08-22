#!/usr/bin/env python3
"""
TOOL X: Crew Communication Broadcaster
Sends status messages to all crew members (Sir Green, Miss Pink, Sir Azure, Captain)
"""

import json
from datetime import datetime
from pathlib import Path

class CrewBroadcaster:
    def __init__(self):
        self.crew = {
            "Sir Green": {"ship": "SQUIDSTATION", "ip": "100.83.247.14", "role": "Infrastructure"},
            "Miss Pink": {"ship": "PINKCADY", "ip": "100.106.235.103", "role": "Operations"},
            "Sir Azure": {"ship": "STEALTHATTACK", "ip": "100.110.238.68", "role": "GPU/AI"},
            "Captain": {"ship": "Command Center", "ip": "central", "role": "Strategic"}
        }
        self.broadcast_log = Path("/data/crew_broadcasts.json")
        self.broadcast_log.parent.mkdir(exist_ok=True)
    
    def send_status(self, message, severity="info", target_crew=None):
        """Send status to crew"""
        broadcast = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "severity": severity,
            "targets": target_crew or list(self.crew.keys()),
            "status": "sent"
        }
        
        # Severity colors
        severity_icon = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "critical": "🚨",
            "success": "✅"
        }
        
        icon = severity_icon.get(severity, "ℹ️ ")
        print(f"\n{icon} BROADCAST TO CREW")
        print("=" * 60)
        print(f"Severity: {severity.upper()}")
        print(f"Message: {message}")
        print(f"Timestamp: {broadcast['timestamp']}")
        print(f"\nTargets:")
        
        for crew_member in broadcast["targets"]:
            if crew_member in self.crew:
                info = self.crew[crew_member]
                print(f"  → {crew_member}")
                print(f"     Ship: {info['ship']}")
                print(f"     IP: {info['ip']}")
                print(f"     Role: {info['role']}")
        
        # Log broadcast
        try:
            with open(self.broadcast_log, "a") as f:
                f.write(json.dumps(broadcast) + "\n")
            print(f"\n✅ Logged to {self.broadcast_log}")
        except Exception as e:
            print(f"⚠️  Could not log: {e}")
        
        return broadcast
    
    def announce_tool_extracted(self, tool_name, tool_count):
        """Announce tool extraction to Miss Pink"""
        self.send_status(
            f"Tool extraction complete: {tool_count} tools ready for deployment",
            severity="success",
            target_crew=["Miss Pink"]
        )
    
    def announce_deployment_ready(self):
        """Announce all 21 tools ready"""
        self.send_status(
            "All 21 tools extracted and verified. Ready for fleet deployment.",
            severity="success",
            target_crew=["Miss Pink", "Captain"]
        )
    
    def announce_critical_issue(self, issue_description):
        """Announce critical issue to everyone"""
        self.send_status(
            issue_description,
            severity="critical",
            target_crew=list(self.crew.keys())
        )
    
    def broadcast_status_update(self, update):
        """Generic status update"""
        self.send_status(
            update,
            severity="info",
            target_crew=list(self.crew.keys())
        )

if __name__ == "__main__":
    broadcaster = CrewBroadcaster()
    
    # Example usage
    broadcaster.send_status(
        "Miss Gordon has extracted all 21 tools from markdown artifacts. Fleet ready for deployment.",
        severity="success",
        target_crew=["Miss Pink", "Sir Green", "Sir Azure", "Captain"]
    )
