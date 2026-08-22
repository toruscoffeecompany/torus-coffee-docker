#!/usr/bin/env python3
"""
TOOL AG: OPSEC Security Audit
Comprehensive security check: Docker API exposure, credentials, network security, TLS, auth
"""

import requests
import json
import socket
import re
from pathlib import Path
from datetime import datetime

class OPSECSecurityAudit:
    def __init__(self):
        self.ships = {
            "SQUIDSTATION": {"ip": "100.83.247.14", "docker_port": 2375},
            "PINKCADY": {"ip": "100.106.235.103", "docker_port": 2375},
            "STEALTHATTACK": {"ip": "100.110.238.68", "docker_port": 2375}
        }
        self.audit_log = Path("/data/opsec_security_audit.json")
        self.audit_log.parent.mkdir(exist_ok=True)
        self.findings = []
    
    def check_docker_api_exposure(self, ship_name, ip, port):
        """Check if Docker API is exposed without TLS/auth"""
        findings = {
            "ship": ship_name,
            "check": "Docker API Exposure",
            "severity": "CRITICAL",
            "issues": []
        }
        
        try:
            # Check if accessible without TLS
            response = requests.get(
                f"http://{ip}:{port}/v1.40/info",
                timeout=5
            )
            
            if response.status_code == 200:
                findings["issues"].append({
                    "issue": "Docker API exposed without TLS",
                    "severity": "CRITICAL",
                    "recommendation": "Enable TLS and client certificates",
                    "command": "dockerd --tlsverify --tlscacert=ca.pem --tlscert=cert.pem --tlskey=key.pem"
                })
            
            # Check if auth enabled
            try:
                # Try unauthenticated container listing
                containers_resp = requests.get(
                    f"http://{ip}:{port}/v1.40/containers/json",
                    timeout=5
                )
                if containers_resp.status_code == 200:
                    findings["issues"].append({
                        "issue": "Docker API accessible without authentication",
                        "severity": "CRITICAL",
                        "recommendation": "Implement authentication/authorization",
                        "action": "Restrict to localhost or use VPN only"
                    })
            except:
                pass
        
        except Exception as e:
            findings["accessible"] = False
        
        return findings
    
    def check_exposed_ports(self, ship_name, ip):
        """Check for exposed ports that shouldn't be public"""
        findings = {
            "ship": ship_name,
            "check": "Exposed Ports",
            "severity": "WARNING",
            "issues": []
        }
        
        dangerous_ports = {
            22: "SSH (should be restricted)",
            2375: "Docker API (should be TLS + auth)",
            2376: "Docker API TLS (should require certs)",
            5000: "Registry (should be behind auth)",
            27017: "MongoDB (should not be exposed)",
            5432: "PostgreSQL (should not be exposed)",
            3306: "MySQL (should not be exposed)",
            6379: "Redis (should not be exposed)",
            9200: "Elasticsearch (should not be exposed)"
        }
        
        for port, description in dangerous_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    findings["issues"].append({
                        "port": port,
                        "service": description,
                        "status": "OPEN",
                        "severity": "CRITICAL" if port in [2375, 22] else "WARNING"
                    })
            except:
                pass
        
        return findings
    
    def check_environment_secrets(self, ship_name, ip, docker_port):
        """Check if credentials are exposed in environment variables"""
        findings = {
            "ship": ship_name,
            "check": "Environment Secret Exposure",
            "severity": "CRITICAL",
            "issues": []
        }
        
        try:
            response = requests.get(
                f"http://{ip}:{docker_port}/v1.40/containers/json",
                timeout=5
            )
            
            if response.status_code == 200:
                containers = response.json()
                
                for container in containers:
                    try:
                        inspect = requests.get(
                            f"http://{ip}:{docker_port}/v1.40/containers/{container['Id']}/json",
                            timeout=5
                        ).json()
                        
                        env_vars = inspect.get("Config", {}).get("Env", [])
                        
                        # Check for secrets in environment
                        secret_patterns = [
                            r"PASSWORD.*=",
                            r"API_KEY.*=",
                            r"SECRET.*=",
                            r"TOKEN.*=",
                            r"DATABASE_URL.*=",
                            r"AWS_SECRET.*="
                        ]
                        
                        for env_var in env_vars:
                            for pattern in secret_patterns:
                                if re.search(pattern, env_var, re.IGNORECASE):
                                    findings["issues"].append({
                                        "container": container.get("Names", ["unknown"])[0],
                                        "issue": "Secret exposed in environment",
                                        "severity": "CRITICAL",
                                        "recommendation": "Use Docker secrets or mounted files, not env vars"
                                    })
                    except:
                        pass
        
        except:
            pass
        
        return findings
    
    def check_network_isolation(self, ship_name, ip, docker_port):
        """Check if containers are properly isolated"""
        findings = {
            "ship": ship_name,
            "check": "Network Isolation",
            "severity": "WARNING",
            "issues": []
        }
        
        try:
            response = requests.get(
                f"http://{ip}:{docker_port}/v1.40/networks",
                timeout=5
            )
            
            if response.status_code == 200:
                networks = response.json()
                
                for network in networks:
                    if network.get("Driver") == "bridge" and network.get("Name") == "bridge":
                        findings["issues"].append({
                            "issue": "Containers on default bridge network",
                            "severity": "WARNING",
                            "recommendation": "Use custom bridge networks for isolation",
                            "benefit": "Better DNS resolution and isolation"
                        })
        
        except:
            pass
        
        return findings
    
    def check_image_vulnerabilities(self, ship_name, ip, docker_port):
        """Check image sources and trust"""
        findings = {
            "ship": ship_name,
            "check": "Image Source Verification",
            "severity": "WARNING",
            "issues": []
        }
        
        try:
            response = requests.get(
                f"http://{ip}:{docker_port}/v1.40/images/json",
                timeout=5
            )
            
            if response.status_code == 200:
                images = response.json()
                
                for image in images:
                    repo_tags = image.get("RepoTags", [])
                    
                    for tag in repo_tags:
                        if tag.startswith("sha256:") or tag == "<none>:<none>":
                            continue
                        
                        # Check for untrusted sources
                        if "localhost" not in tag and "private-registry" not in tag:
                            if tag.count("/") == 0:  # Docker Hub official images
                                findings["issues"].append({
                                    "image": tag,
                                    "issue": "No image signing/verification",
                                    "recommendation": "Consider using Docker Content Trust",
                                    "severity": "INFO"
                                })
        
        except:
            pass
        
        return findings
    
    def run_full_audit(self):
        """Run complete OPSEC security audit"""
        print("\n🔒 OPSEC SECURITY AUDIT")
        print("=" * 80)
        
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "audit_type": "OPSEC_security_check",
            "ships": [],
            "summary": {
                "critical_issues": 0,
                "warning_issues": 0,
                "info_issues": 0
            }
        }
        
        for ship_name, ship_info in self.ships.items():
            print(f"\n🔍 Auditing {ship_name}...")
            
            ship_audit = {
                "ship": ship_name,
                "checks": []
            }
            
            # Run all checks
            checks = [
                self.check_docker_api_exposure(ship_name, ship_info["ip"], ship_info["docker_port"]),
                self.check_exposed_ports(ship_name, ship_info["ip"]),
                self.check_environment_secrets(ship_name, ship_info["ip"], ship_info["docker_port"]),
                self.check_network_isolation(ship_name, ship_info["ip"], ship_info["docker_port"]),
                self.check_image_vulnerabilities(ship_name, ship_info["ip"], ship_info["docker_port"])
            ]
            
            for check in checks:
                ship_audit["checks"].append(check)
                
                # Count issues by severity
                for issue in check.get("issues", []):
                    severity = issue.get("severity", "INFO")
                    if severity == "CRITICAL":
                        audit["summary"]["critical_issues"] += 1
                        print(f"  🚨 {check['check']}: {issue.get('issue', 'Unknown')}")
                    elif severity == "WARNING":
                        audit["summary"]["warning_issues"] += 1
                        print(f"  ⚠️  {check['check']}: {issue.get('issue', 'Unknown')}")
            
            audit["ships"].append(ship_audit)
        
        # Overall assessment
        print("\n" + "=" * 80)
        print("🛡️  SECURITY ASSESSMENT")
        print("=" * 80)
        print(f"🚨 Critical Issues: {audit['summary']['critical_issues']}")
        print(f"⚠️  Warning Issues: {audit['summary']['warning_issues']}")
        print(f"ℹ️  Info Issues: {audit['summary']['info_issues']}")
        
        if audit['summary']['critical_issues'] > 0:
            print(f"\n❌ SECURITY POSTURE: AT RISK")
            print("Immediate action required for critical issues")
        else:
            print(f"\n✅ SECURITY POSTURE: ACCEPTABLE")
        
        # Recommendations
        print("\n📋 TOP RECOMMENDATIONS:")
        print("  1. Enable TLS for Docker API (use certificates)")
        print("  2. Implement authentication for Docker API")
        print("  3. Restrict Docker API to localhost or VPN only")
        print("  4. Use Docker secrets instead of environment variables")
        print("  5. Scan images regularly for vulnerabilities")
        print("  6. Implement network policies between containers")
        
        # Save audit
        with open(self.audit_log, 'w') as f:
            json.dump(audit, f, indent=2)
        
        print(f"\n📋 Audit saved to {self.audit_log}")
        
        return audit

if __name__ == "__main__":
    auditor = OPSECSecurityAudit()
    auditor.run_full_audit()
