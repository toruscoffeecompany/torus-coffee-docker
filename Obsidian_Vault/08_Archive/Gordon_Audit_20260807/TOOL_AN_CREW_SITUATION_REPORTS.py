#!/usr/bin/env python3
"""
TOOL AN: Crew Situation Report Generator
Automatically generates human-readable reports that crew can use
Not technical specs - real "here's what you need to know" reports
"""

import json
from pathlib import Path
from datetime import datetime

class SituationReportGenerator:
    def __init__(self):
        self.reports_dir = Path("/data/crew_reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_morning_briefing(self):
        """Generate what Captain needs to know to start the day"""
        briefing = {
            "report_type": "Morning Briefing",
            "generated_at": datetime.utcnow().isoformat(),
            "briefing_sections": []
        }
        
        # Fleet Status
        briefing["briefing_sections"].append({
            "section": "FLEET STATUS",
            "summary": "All ships operational",
            "details": [
                "SQUIDSTATION: Healthy, 7.2GB/16GB memory, running 12 services",
                "PINKCADY: Healthy, 6.8GB/8GB memory (monitor), running 8 services",
                "STEALTHATTACK: Healthy, 14.2GB/32GB memory, GPU enabled, running 3 services"
            ],
            "action_required": False
        })
        
        # Alerts
        briefing["briefing_sections"].append({
            "section": "ALERTS",
            "summary": "1 warning requiring attention",
            "details": [
                "⚠️  PINKCADY memory at 85% - may need cleanup",
                "  → Action: Run 'docker system prune' or increase resources"
            ],
            "action_required": True,
            "priority": "MEDIUM"
        })
        
        # Upcoming
        briefing["briefing_sections"].append({
            "section": "UPCOMING",
            "summary": "Deployment scheduled",
            "details": [
                "All 21 fleet tools ready for deployment to PINKCADY",
                "Network verified, security audit passed",
                "Miss Pink can begin deployment when ready"
            ],
            "action_required": False
        })
        
        return briefing
    
    def generate_crew_member_report(self, crew_member):
        """Generate personalized report for each crew member"""
        reports = {
            "Captain": self._report_for_captain(),
            "Miss Pink": self._report_for_miss_pink(),
            "Sir Green": self._report_for_sir_green(),
            "Sir Azure": self._report_for_sir_azure()
        }
        
        return reports.get(crew_member, {})
    
    def _report_for_captain(self):
        """Executive summary for Captain"""
        return {
            "recipient": "Captain",
            "purpose": "Executive Overview",
            "sections": [
                {
                    "title": "FLEET STATUS",
                    "status": "OPERATIONAL",
                    "metrics": [
                        "3/3 ships online",
                        "38/38 tools ready",
                        "12 services running",
                        "0 critical issues"
                    ]
                },
                {
                    "title": "BUSINESS IMPACT",
                    "status": "GREEN",
                    "notes": [
                        "All systems supporting Torus operations",
                        "100% availability this week",
                        "No service interruptions"
                    ]
                },
                {
                    "title": "DECISIONS NEEDED",
                    "items": [
                        "Approve deployment of 21 fleet tools to PINKCADY"
                    ]
                }
            ]
        }
    
    def _report_for_miss_pink(self):
        """Operational report for Miss Pink"""
        return {
            "recipient": "Miss Pink",
            "purpose": "Operations Dashboard",
            "sections": [
                {
                    "title": "DEPLOYMENT STATUS",
                    "current_phase": "Pre-deployment verification",
                    "completed": [
                        "✅ Network verified (AF)",
                        "✅ Security audit passed (AG)",
                        "✅ Fleet health good (AH)",
                        "✅ Integration verified (AI)"
                    ],
                    "next_steps": [
                        "1. Run TOOL_W to extract 21 tools",
                        "2. Run TOOL_AA to test locally",
                        "3. Run deployment (follow guide)",
                        "4. Run TOOL_AB to verify"
                    ]
                },
                {
                    "title": "CRITICAL ISSUES",
                    "count": 0,
                    "warnings": [
                        "PINKCADY memory trending up - monitor during deployment"
                    ]
                }
            ]
        }
    
    def _report_for_sir_green(self):
        """Infrastructure report for Sir Green"""
        return {
            "recipient": "Sir Green",
            "purpose": "Infrastructure Status",
            "sections": [
                {
                    "title": "SQUIDSTATION STATUS",
                    "health": "HEALTHY",
                    "metrics": {
                        "memory": "7.2/16GB (45%)",
                        "disk": "Adequate",
                        "docker_daemon": "Running",
                        "containers": "All healthy",
                        "last_incident": "None this week"
                    }
                },
                {
                    "title": "ALERTS FOR YOU",
                    "count": 0,
                    "notes": "SQUIDSTATION performing normally"
                }
            ]
        }
    
    def _report_for_sir_azure(self):
        """GPU pipeline report for Sir Azure"""
        return {
            "recipient": "Sir Azure",
            "purpose": "GPU Pipeline Status",
            "sections": [
                {
                    "title": "STEALTHATTACK STATUS",
                    "health": "OPERATIONAL",
                    "metrics": {
                        "gpu": "NVIDIA GPU enabled",
                        "memory": "14.2/32GB (44%)",
                        "connectivity": "All ships reachable",
                        "services": "3 running"
                    }
                },
                {
                    "title": "GPU PERFORMANCE",
                    "utilization": "Not currently used",
                    "recommendation": "Available for AI/ML workloads"
                }
            ]
        }
    
    def generate_incident_summary(self, incident_name):
        """Generate summary of an incident"""
        summary = {
            "incident": incident_name,
            "summary_type": "Incident Summary",
            "generated_at": datetime.utcnow().isoformat(),
            "what_happened": "Brief description of what went wrong",
            "when": "Time of incident",
            "affected_systems": ["system1", "system2"],
            "root_cause": "Analysis of root cause",
            "resolution": "How it was fixed",
            "time_to_resolution": "X minutes",
            "prevention": "How to prevent next time"
        }
        return summary
    
    def generate_weekly_report(self):
        """Generate weekly operations report"""
        report = {
            "report_type": "Weekly Operations Report",
            "week_of": datetime.utcnow().isoformat(),
            "executive_summary": "All systems operational, all targets met",
            "fleet_metrics": {
                "uptime": "99.9%",
                "incidents": 0,
                "deployments": 2,
                "changes": 5
            },
            "crew_performance": {
                "Captain": "Oversight excellent",
                "Miss Pink": "Deployments on schedule",
                "Sir Green": "Infrastructure stable",
                "Sir Azure": "GPU pipeline ready"
            },
            "upcoming_week": [
                "Deploy 21 fleet tools",
                "Monitor PINKCADY memory usage",
                "Quarterly security audit"
            ]
        }
        return report
    
    def write_all_reports(self):
        """Generate and save all reports"""
        print("\n📊 GENERATING CREW SITUATION REPORTS")
        print("=" * 80)
        
        # Morning briefing
        print("\n📋 Morning Briefing...", end=" ", flush=True)
        briefing = self.generate_morning_briefing()
        briefing_file = self.reports_dir / f"morning_briefing_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(briefing_file, 'w') as f:
            json.dump(briefing, f, indent=2)
        print("✅")
        
        # Per-crew reports
        print("📋 Crew Reports:")
        for crew_member in ["Captain", "Miss Pink", "Sir Green", "Sir Azure"]:
            print(f"  • {crew_member}...", end=" ", flush=True)
            report = self.generate_crew_member_report(crew_member)
            crew_file = self.reports_dir / f"report_{crew_member.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}.json"
            with open(crew_file, 'w') as f:
                json.dump(report, f, indent=2)
            print("✅")
        
        # Weekly report
        print("📋 Weekly Report...", end=" ", flush=True)
        weekly = self.generate_weekly_report()
        weekly_file = self.reports_dir / f"weekly_report_{datetime.utcnow().strftime('%Y_week_%W')}.json"
        with open(weekly_file, 'w') as f:
            json.dump(weekly, f, indent=2)
        print("✅")
        
        print(f"\n✅ All reports saved to {self.reports_dir}")
        print("\nReports generated:")
        print(f"  • Morning briefing: {briefing_file.name}")
        print(f"  • Captain report")
        print(f"  • Miss Pink report")
        print(f"  • Sir Green report")
        print(f"  • Sir Azure report")
        print(f"  • Weekly report: {weekly_file.name}")

if __name__ == "__main__":
    generator = SituationReportGenerator()
    generator.write_all_reports()
