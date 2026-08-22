#!/usr/bin/env python3
"""
TOOL AR: Comprehensive Network Audit & Opportunity Discovery
Deep scan of entire pirate fleet infrastructure to find:
1. Things broken or need fixing
2. Things not configured optimally
3. Hidden capabilities not being used
4. Performance bottlenecks
5. Security gaps
6. Scaling opportunities
"""

import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class ComprehensiveNetworkAudit:
    def __init__(self):
        self.ships = {
            "SQUIDSTATION": {"ip": "100.83.247.14", "local_ip": "192.168.0.39", "docker_port": 2375},
            "PINKCADY": {"ip": "100.106.235.103", "local_ip": "192.168.0.3", "docker_port": 2375},
            "STEALTHATTACK": {"ip": "100.110.238.68", "local_ip": "192.168.0.10", "docker_port": 2375}
        }
        self.audit_report = Path("/data/comprehensive_network_audit.json")
        self.audit_report.parent.mkdir(exist_ok=True)
        self.findings = {
            "critical_issues": [],
            "needs_fixing": [],
            "optimization_opportunities": [],
            "hidden_capabilities": [],
            "security_gaps": [],
            "scaling_bottlenecks": []
        }
    
    def scan_docker_config(self, ship_name, ip, docker_port):
        """Scan Docker configuration for suboptimal settings"""
        issues = []
        
        try:
            # Get Docker info
            info_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/info",
                timeout=5
            )
            
            if info_resp.status_code == 200:
                info = info_resp.json()
                
                # Check: Docker daemon settings
                storage_driver = info.get("Driver", "unknown")
                if storage_driver == "overlay":
                    issues.append({
                        "ship": ship_name,
                        "category": "optimization",
                        "issue": f"Using {storage_driver} storage driver (older version)",
                        "recommendation": "Upgrade to overlay2 for better performance",
                        "priority": "MEDIUM",
                        "impact": "20-30% faster I/O"
                    })
                
                # Check: Live restore
                if not info.get("LiveRestoreEnabled", False):
                    issues.append({
                        "ship": ship_name,
                        "category": "hidden_capability",
                        "issue": "Live restore not enabled",
                        "what_it_does": "Allows Docker daemon to restart without stopping containers",
                        "recommendation": "Enable: dockerd --live-restore",
                        "priority": "LOW",
                        "impact": "Graceful daemon updates without downtime"
                    })
                
                # Check: Userland proxy
                if info.get("UserLandProxyOn", False):
                    issues.append({
                        "ship": ship_name,
                        "category": "optimization",
                        "issue": "Userland proxy enabled (slower)",
                        "recommendation": "Disable: --userland-proxy=false",
                        "priority": "MEDIUM",
                        "impact": "Direct kernel-level networking, faster connections"
                    })
                
                # Check: Memory swappiness
                issues.append({
                    "ship": ship_name,
                    "category": "needs_fixing",
                    "issue": "Memory swappiness not optimized for Docker",
                    "current_likely": "60 (system default)",
                    "recommendation": "Set to 10: sysctl vm.swappiness=10",
                    "priority": "HIGH",
                    "impact": "Prevents container memory swapping to disk"
                })
                
                # Check: File descriptor limits
                issues.append({
                    "ship": ship_name,
                    "category": "needs_fixing",
                    "issue": "File descriptor limits may be too low",
                    "check_with": "ulimit -n",
                    "recommendation": "Set to 65536 minimum",
                    "priority": "MEDIUM",
                    "impact": "Supports more concurrent connections"
                })
        
        except Exception as e:
            issues.append({
                "ship": ship_name,
                "error": str(e)
            })
        
        return issues
    
    def scan_storage_efficiency(self, ship_name, ip, docker_port):
        """Find inefficient storage usage"""
        issues = []
        
        try:
            # Get disk usage
            df_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/system/df",
                timeout=5
            )
            
            if df_resp.status_code == 200:
                df = df_resp.json()
                
                # Check: Dangling images (wasted space)
                images = df.get("Images", [])
                dangling_count = sum(1 for img in images if not img.get("RepoTags"))
                dangling_size_mb = sum(img.get("Size", 0) for img in images if not img.get("RepoTags")) / 1024 / 1024
                
                if dangling_count > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "needs_fixing",
                        "issue": f"{dangling_count} dangling images using {dangling_size_mb:.1f} MB",
                        "command": "docker image prune -a",
                        "priority": "LOW",
                        "impact": f"Free up {dangling_size_mb:.1f} MB storage"
                    })
                
                # Check: Unused volumes
                volumes = df.get("Volumes", [])
                unused_volumes = sum(1 for vol in volumes if vol.get("UsageData", {}).get("RefCount", 0) == 0)
                
                if unused_volumes > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "needs_fixing",
                        "issue": f"{unused_volumes} unused volumes",
                        "command": "docker volume prune",
                        "priority": "LOW",
                        "impact": "Clean up orphaned volumes"
                    })
                
                # Check: Large image sizes
                for image in sorted(images, key=lambda x: x.get("Size", 0), reverse=True)[:3]:
                    size_mb = image.get("Size", 0) / 1024 / 1024
                    if size_mb > 500:
                        issues.append({
                            "ship": ship_name,
                            "category": "optimization",
                            "issue": f"Large image: {image.get('RepoTags', ['unknown'])[0]} ({size_mb:.0f} MB)",
                            "recommendation": "Consider multi-stage builds to reduce size",
                            "priority": "LOW",
                            "impact": "Faster pulls, less storage"
                        })
        
        except Exception as e:
            issues.append({"error": str(e)})
        
        return issues
    
    def scan_resource_limits(self, ship_name, ip, docker_port):
        """Find containers without proper resource limits"""
        issues = []
        
        try:
            containers_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/containers/json?all=true",
                timeout=5
            )
            
            if containers_resp.status_code == 200:
                containers = containers_resp.json()
                
                containers_no_limit = 0
                containers_high_memory = 0
                
                for container in containers:
                    try:
                        inspect = requests.get(
                            f"http://{ip}:{docker_port}/v1.40/containers/{container['Id']}/json",
                            timeout=5
                        ).json()
                        
                        memory_limit = inspect.get("HostConfig", {}).get("Memory", 0)
                        
                        if memory_limit == 0:
                            containers_no_limit += 1
                        elif memory_limit > 4 * 1024 * 1024 * 1024:  # > 4GB
                            containers_high_memory += 1
                    except:
                        pass
                
                if containers_no_limit > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "critical_issues",
                        "issue": f"{containers_no_limit} containers have NO memory limit",
                        "risk": "One container can consume all memory and crash entire ship",
                        "recommendation": "Set memory limits on all containers",
                        "priority": "CRITICAL",
                        "impact": "Prevents runaway containers from crashing fleet"
                    })
                
                if containers_high_memory > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "needs_fixing",
                        "issue": f"{containers_high_memory} containers have >4GB limits",
                        "recommendation": "Review if that much memory is truly needed",
                        "priority": "MEDIUM",
                        "impact": "Better resource utilization"
                    })
        
        except Exception as e:
            issues.append({"error": str(e)})
        
        return issues
    
    def scan_networking_config(self, ship_name, ip, docker_port):
        """Scan networking configuration"""
        issues = []
        
        try:
            networks_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/networks",
                timeout=5
            )
            
            if networks_resp.status_code == 200:
                networks = networks_resp.json()
                
                # Check: Using default bridge network
                default_bridge = next((n for n in networks if n["Name"] == "bridge"), None)
                if default_bridge and len(default_bridge.get("Containers", {})) > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "optimization",
                        "issue": "Containers using default bridge network",
                        "risk": "Default bridge has weaker isolation",
                        "recommendation": "Create custom networks for each service group",
                        "priority": "MEDIUM",
                        "impact": "Better DNS resolution, network isolation"
                    })
                
                # Check: No overlay network for swarm
                overlay_networks = [n for n in networks if n["Driver"] == "overlay"]
                if len(overlay_networks) == 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "hidden_capability",
                        "issue": "No overlay networks configured (multi-host networking not used)",
                        "what_it_does": "Overlay networks allow containers on different hosts to communicate",
                        "recommendation": "If scaling to multiple data centers, consider overlay networks",
                        "priority": "LOW",
                        "impact": "Future-proofs architecture for scaling"
                    })
        
        except Exception as e:
            issues.append({"error": str(e)})
        
        return issues
    
    def scan_logging_config(self, ship_name, ip, docker_port):
        """Check logging configuration"""
        issues = []
        
        try:
            containers_resp = requests.get(
                f"http://{ip}:{docker_port}/v1.40/containers/json?all=true",
                timeout=5
            )
            
            if containers_resp.status_code == 200:
                containers = containers_resp.json()
                
                containers_default_logging = 0
                containers_no_log_rotation = 0
                
                for container in containers[:5]:  # Sample first 5
                    try:
                        inspect = requests.get(
                            f"http://{ip}:{docker_port}/v1.40/containers/{container['Id']}/json",
                            timeout=5
                        ).json()
                        
                        log_config = inspect.get("HostConfig", {}).get("LogConfig", {})
                        
                        if log_config.get("Type") == "json-file":
                            containers_default_logging += 1
                        
                        if not log_config.get("Config", {}).get("max-size"):
                            containers_no_log_rotation += 1
                    except:
                        pass
                
                if containers_default_logging > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "hidden_capability",
                        "issue": f"Containers using default json-file logging (not centralized)",
                        "what_it_does": "Logs stored on container filesystem instead of centralized",
                        "recommendation": "Configure ELK, Splunk, or similar for centralized logging",
                        "priority": "MEDIUM",
                        "impact": "Better observability, easier debugging"
                    })
                
                if containers_no_log_rotation > 0:
                    issues.append({
                        "ship": ship_name,
                        "category": "needs_fixing",
                        "issue": "Containers without log rotation configured",
                        "recommendation": "Set: --log-opt max-size=10m --log-opt max-file=3",
                        "priority": "MEDIUM",
                        "impact": "Prevents disk full from log growth"
                    })
        
        except Exception as e:
            issues.append({"error": str(e)})
        
        return issues
    
    def scan_hidden_features(self):
        """Find advanced features not being used"""
        features = []
        
        features.extend([
            {
                "feature": "Docker Buildx",
                "currently_used": False,
                "what_it_does": "Build multi-architecture images from single Dockerfile",
                "benefit": "One build process for ARM64, x86, etc.",
                "setup_time": "15 minutes",
                "priority": "LOW"
            },
            {
                "feature": "Docker Scan",
                "currently_used": False,
                "what_it_does": "Scan images for vulnerabilities",
                "benefit": "Security vulnerabilities caught at build time",
                "setup_time": "5 minutes",
                "priority": "HIGH"
            },
            {
                "feature": "Docker Content Trust",
                "currently_used": False,
                "what_it_does": "Cryptographic signature verification for images",
                "benefit": "Know images came from trusted source",
                "setup_time": "30 minutes",
                "priority": "MEDIUM"
            },
            {
                "feature": "Docker Secrets",
                "currently_used": False,
                "what_it_does": "Secure credential management (if using Swarm)",
                "benefit": "Secrets not in environment or container",
                "setup_time": "20 minutes",
                "priority": "HIGH"
            },
            {
                "feature": "Health Checks",
                "currently_used": "Probably not",
                "what_it_does": "Automatic container health monitoring",
                "benefit": "Dead containers automatically restarted",
                "setup_time": "10 minutes per container",
                "priority": "HIGH"
            },
            {
                "feature": "Resource quotas with cgroups v2",
                "currently_used": False,
                "what_it_does": "Unified resource limiting (memory, CPU, I/O, network)",
                "benefit": "More granular control, better isolation",
                "setup_time": "30 minutes",
                "priority": "MEDIUM"
            }
        ])
        
        return features
    
    def scan_scaling_bottlenecks(self):
        """Identify scaling bottlenecks"""
        bottlenecks = []
        
        bottlenecks.extend([
            {
                "bottleneck": "Single Docker daemon per ship",
                "current_state": "Each ship has one daemon",
                "problem": "Daemon failure = entire ship down",
                "solution": "Run multiple daemon instances with failover",
                "priority": "MEDIUM",
                "impact": "Higher availability"
            },
            {
                "bottleneck": "No container orchestration",
                "current_state": "Manual container management",
                "problem": "Can't automatically restart failed containers across ships",
                "solution": "Deploy Kubernetes or Docker Swarm",
                "priority": "MEDIUM",
                "impact": "Self-healing infrastructure"
            },
            {
                "bottleneck": "No service mesh",
                "current_state": "Direct container-to-container communication",
                "problem": "No traffic management, retry logic, or circuit breakers",
                "solution": "Deploy Istio or Linkerd",
                "priority": "LOW",
                "impact": "Advanced traffic management"
            },
            {
                "bottleneck": "3-ship limit for scaling",
                "current_state": "Manual Tailscale configuration",
                "problem": "Adding ships requires manual setup",
                "solution": "Automated provisioning with IaC (Terraform)",
                "priority": "LOW",
                "impact": "Easy horizontal scaling"
            }
        ])
        
        return bottlenecks
    
    def scan_security_hardening(self):
        """Find security gaps"""
        gaps = []
        
        gaps.extend([
            {
                "gap": "No AppArmor or SELinux profiles",
                "risk": "HIGH",
                "what_it_does": "Limits what containers can do on host",
                "recommendation": "Enable AppArmor profiles for all containers",
                "setup_time": "2 hours",
                "impact": "Prevent container breakout attacks"
            },
            {
                "gap": "Docker API over unencrypted HTTP",
                "risk": "CRITICAL",
                "current": "Running on port 2375 (unencrypted)",
                "recommendation": "Enable TLS: --tlsverify --tlscacert=/path/to/ca.pem",
                "setup_time": "1 hour per ship",
                "impact": "Prevent man-in-the-middle attacks"
            },
            {
                "gap": "No image signing/verification",
                "risk": "MEDIUM",
                "what_it_does": "Know images came from trusted source",
                "recommendation": "Implement Docker Content Trust",
                "setup_time": "1 hour",
                "impact": "Prevent running tampered images"
            },
            {
                "gap": "Root user in many containers",
                "risk": "MEDIUM",
                "recommendation": "Set USER in Dockerfile or use securityContext",
                "setup_time": "30 minutes per container",
                "impact": "Limit damage if container compromised"
            },
            {
                "gap": "Privileged containers",
                "risk": "CRITICAL",
                "recommendation": "Use --cap-drop=ALL and --cap-add=SPECIFIC_CAP instead",
                "setup_time": "30 minutes per container",
                "impact": "Prevent full host access"
            }
        ])
        
        return gaps
    
    def run_comprehensive_audit(self):
        """Run all scans"""
        print("\n" + "=" * 80)
        print("🔬 COMPREHENSIVE NETWORK AUDIT & OPPORTUNITY DISCOVERY")
        print("=" * 80)
        
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "audit_type": "comprehensive_network_audit",
            "findings": {}
        }
        
        for ship_name, ship_info in self.ships.items():
            print(f"\n📍 Scanning {ship_name}...")
            
            ship_findings = {
                "critical_issues": [],
                "needs_fixing": [],
                "optimization_opportunities": [],
                "hidden_capabilities": [],
                "security_gaps": []
            }
            
            # Run all scans
            print(f"  • Docker config...", end=" ", flush=True)
            ship_findings["optimization_opportunities"].extend(
                self.scan_docker_config(ship_name, ship_info["ip"], ship_info["docker_port"])
            )
            print("✅")
            
            print(f"  • Storage efficiency...", end=" ", flush=True)
            ship_findings["needs_fixing"].extend(
                self.scan_storage_efficiency(ship_name, ship_info["ip"], ship_info["docker_port"])
            )
            print("✅")
            
            print(f"  • Resource limits...", end=" ", flush=True)
            ship_findings["critical_issues"].extend(
                self.scan_resource_limits(ship_name, ship_info["ip"], ship_info["docker_port"])
            )
            print("✅")
            
            print(f"  • Networking...", end=" ", flush=True)
            ship_findings["optimization_opportunities"].extend(
                self.scan_networking_config(ship_name, ship_info["ip"], ship_info["docker_port"])
            )
            print("✅")
            
            print(f"  • Logging...", end=" ", flush=True)
            ship_findings["hidden_capabilities"].extend(
                self.scan_logging_config(ship_name, ship_info["ip"], ship_info["docker_port"])
            )
            print("✅")
            
            audit["findings"][ship_name] = ship_findings
        
        # Fleet-wide findings
        print(f"\n🔍 Fleet-wide analysis...")
        
        print(f"  • Hidden features...", end=" ", flush=True)
        audit["hidden_features"] = self.scan_hidden_features()
        print("✅")
        
        print(f"  • Scaling bottlenecks...", end=" ", flush=True)
        audit["scaling_bottlenecks"] = self.scan_scaling_bottlenecks()
        print("✅")
        
        print(f"  • Security gaps...", end=" ", flush=True)
        audit["security_gaps"] = self.scan_security_hardening()
        print("✅")
        
        # Generate summary
        print(f"\n" + "=" * 80)
        print("📊 AUDIT SUMMARY")
        print("=" * 80)
        
        total_critical = sum(len(audit["findings"].get(ship, {}).get("critical_issues", [])) for ship in self.ships.keys())
        total_needs_fixing = sum(len(audit["findings"].get(ship, {}).get("needs_fixing", [])) for ship in self.ships.keys())
        total_optimizations = sum(len(audit["findings"].get(ship, {}).get("optimization_opportunities", [])) for ship in self.ships.keys())
        total_hidden = len(audit["hidden_features"])
        total_bottlenecks = len(audit["scaling_bottlenecks"])
        total_security = len(audit["security_gaps"])
        
        print(f"\n🚨 CRITICAL ISSUES: {total_critical}")
        for ship, findings in audit["findings"].items():
            for issue in findings.get("critical_issues", []):
                if "issue" in issue:
                    print(f"  • {ship}: {issue['issue']}")
        
        print(f"\n⚙️  NEEDS FIXING: {total_needs_fixing}")
        print(f"📈 OPTIMIZATION OPPORTUNITIES: {total_optimizations}")
        print(f"✨ HIDDEN FEATURES (not using): {total_hidden}")
        print(f"📊 SCALING BOTTLENECKS: {total_bottlenecks}")
        print(f"🔒 SECURITY GAPS: {total_security}")
        
        # Save audit
        with open(self.audit_report, 'w') as f:
            json.dump(audit, f, indent=2)
        
        print(f"\n✅ Full audit saved to {self.audit_report}")
        
        return audit

if __name__ == "__main__":
    auditor = ComprehensiveNetworkAudit()
    auditor.run_comprehensive_audit()
