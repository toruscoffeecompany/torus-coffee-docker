#!/usr/bin/env python3
"""
TOOL AU: Deep System Analysis & Hardware Inventory
Complete hardware and software deep dive across entire fleet
"""

import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

class DeepSystemAnalysis:
    def __init__(self):
        self.analysis_report = Path("/data/deep_system_analysis.json")
        self.analysis_report.parent.mkdir(exist_ok=True)
        self.ships = {
            "SQUIDSTATION": "100.83.247.14",
            "PINKCADY": "100.106.235.103",
            "STEALTHATTACK": "100.110.238.68"
        }
    
    def analyze_hardware_inventory(self):
        """Deep hardware analysis"""
        inventory = {
            "timestamp": datetime.utcnow().isoformat(),
            "hardware_analysis": {}
        }
        
        print("\n💾 DEEP HARDWARE ANALYSIS")
        print("=" * 80)
        
        # Local system analysis
        print("\n🖥️  Local System:")
        try:
            # CPU info
            result = subprocess.run(["nproc"], capture_output=True, text=True, timeout=5)
            cpus = result.stdout.strip()
            print(f"  CPUs: {cpus}")
            
            # Memory
            result = subprocess.run(
                ["free", "-g"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                memory_line = lines[1].split()
                total_mem = memory_line[1]
                print(f"  Memory: {total_mem}GB total")
            
            # Disk
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                disk_line = lines[1].split()
                disk_total = disk_line[1]
                disk_used = disk_line[2]
                print(f"  Disk: {disk_total} total, {disk_used} used")
            
            # GPU detection
            print("\n  GPU Detection:")
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "NVIDIA" in result.stdout or "AMD" in result.stdout or "Intel" in result.stdout:
                gpu_lines = [line for line in result.stdout.split('\n') if 'VGA' in line or 'GPU' in line or '3D' in line]
                for gpu in gpu_lines[:3]:
                    print(f"    • {gpu}")
            else:
                print("    No dedicated GPU detected")
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return inventory
    
    def analyze_docker_configuration(self):
        """Deep Docker configuration analysis"""
        analysis = {
            "docker_daemon": {},
            "storage_backend": {},
            "networking": {},
            "security": {},
            "performance": {}
        }
        
        print("\n🐳 DEEP DOCKER CONFIGURATION ANALYSIS")
        print("=" * 80)
        
        try:
            # Get full docker info
            result = subprocess.run(
                ["docker", "info", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                # Storage backend
                print(f"\n  Storage Driver: {info.get('Driver', 'unknown')}")
                analysis["storage_backend"]["driver"] = info.get('Driver')
                analysis["storage_backend"]["data_space"] = info.get('DriverStatus', {})
                
                # Networking
                print(f"  Network Mode: {info.get('DefaultRuntime', 'runc')}")
                
                # Security
                print(f"  Security Options: {info.get('SecurityOptions', 'none')}")
                analysis["security"]["options"] = info.get('SecurityOptions', [])
                
                # Cgroup version
                cgroup_version = "v1" if "cgroup2" not in str(info) else "v2"
                print(f"  Cgroup Version: {cgroup_version}")
                analysis["performance"]["cgroup_version"] = cgroup_version
                
                # Swarm
                swarm_status = info.get('Swarm', {}).get('LocalNodeState', 'inactive')
                print(f"  Swarm Status: {swarm_status}")
                
                # API version
                api_version = info.get('ServerVersion', 'unknown')
                print(f"  API Version: {api_version}")
                analysis["docker_daemon"]["api_version"] = api_version
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return analysis
    
    def analyze_running_services(self):
        """Analyze all running services and containers"""
        services = {
            "services": [],
            "system_services": [],
            "containers": [],
            "opportunities": []
        }
        
        print("\n🔍 RUNNING SERVICES DEEP ANALYSIS")
        print("=" * 80)
        
        try:
            # Docker containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            containers = result.stdout.strip().split('\n')
            print(f"\n  Running Containers ({len(containers)}):")
            
            for container in containers[:10]:  # Show first 10
                if container:
                    print(f"    • {container}")
                    services["containers"].append(container)
            
            # System services
            print("\n  System Services:")
            critical_services = [
                "docker",
                "tailscale",
                "systemd-resolved",
                "cron",
                "ssh"
            ]
            
            for service in critical_services:
                try:
                    result = subprocess.run(
                        ["systemctl", "is-active", service],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    status = "✅ Running" if result.returncode == 0 else "❌ Stopped"
                    print(f"    • {service}: {status}")
                    services["system_services"].append({
                        "service": service,
                        "status": "running" if result.returncode == 0 else "stopped"
                    })
                except:
                    pass
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return services
    
    def analyze_network_topology(self):
        """Analyze complete network topology"""
        topology = {
            "interfaces": [],
            "routes": [],
            "dns_config": {},
            "firewall": {},
            "vpn_status": {}
        }
        
        print("\n🌐 NETWORK TOPOLOGY DEEP ANALYSIS")
        print("=" * 80)
        
        try:
            # Network interfaces
            print("\n  Network Interfaces:")
            result = subprocess.run(
                ["ip", "addr"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            interfaces = re.findall(r'\d+:\s+(\w+).*inet\s+(\S+)', result.stdout)
            for iface, ip in interfaces:
                print(f"    • {iface}: {ip}")
                topology["interfaces"].append({"interface": iface, "ip": ip})
            
            # DNS
            print("\n  DNS Configuration:")
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    dns_lines = [line.strip() for line in f if 'nameserver' in line]
                    for dns in dns_lines[:3]:
                        print(f"    • {dns}")
                        topology["dns_config"]["nameservers"] = dns_lines
            except:
                pass
            
            # Tailscale status
            print("\n  Tailscale VPN:")
            result = subprocess.run(
                ["tailscale", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "Tailscale is running" in result.stdout or "100." in result.stdout:
                print("    ✅ Tailscale ACTIVE")
                topology["vpn_status"]["tailscale"] = "active"
                # Extract IPs
                ips = re.findall(r'100\.\d+\.\d+\.\d+', result.stdout)
                if ips:
                    print(f"    Peers: {len(ips)}")
                    topology["vpn_status"]["peer_count"] = len(ips)
            else:
                print("    ⚠️  Tailscale status unclear")
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return topology
    
    def analyze_storage_subsystem(self):
        """Deep storage analysis"""
        storage = {
            "mounts": [],
            "usage": {},
            "optimization_opportunities": [],
            "docker_storage": {}
        }
        
        print("\n💾 STORAGE SUBSYSTEM DEEP ANALYSIS")
        print("=" * 80)
        
        try:
            # Mount points
            print("\n  Mounted Filesystems:")
            result = subprocess.run(
                ["mount"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            mounts = result.stdout.strip().split('\n')
            for mount in mounts[:5]:  # Show first 5
                if 'type' in mount:
                    print(f"    • {mount}")
            
            # Disk usage
            print("\n  Disk Usage by Directory:")
            result = subprocess.run(
                ["du", "-sh", "/var/lib/docker/", "/home/", "/opt/"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"    • {line}")
            
            # Docker storage location
            print("\n  Docker Storage:")
            result = subprocess.run(
                ["docker", "info", "--format", "{{.DockerRootDir}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            docker_root = result.stdout.strip()
            print(f"    Root Dir: {docker_root}")
            storage["docker_storage"]["root_dir"] = docker_root
            
            # Check if on separate mount
            if docker_root.startswith('/mnt/') or docker_root.startswith('/data/'):
                print(f"    ✅ Docker on separate mount (GOOD)")
                storage["docker_storage"]["optimization"] = "separate_mount"
            else:
                print(f"    ⚠️  Docker on root filesystem (consider moving)")
                storage["docker_storage"]["optimization"] = "move_to_separate_mount"
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return storage
    
    def identify_performance_bottlenecks(self):
        """Identify potential bottlenecks"""
        bottlenecks = []
        
        print("\n⚡ PERFORMANCE BOTTLENECK ANALYSIS")
        print("=" * 80)
        
        try:
            # Check load average
            print("\n  System Load:")
            with open('/proc/loadavg', 'r') as f:
                load = f.read().split()
                load_1, load_5, load_15 = load[0], load[1], load[2]
                print(f"    1min: {load_1}, 5min: {load_5}, 15min: {load_15}")
                
                try:
                    nproc = int(subprocess.run(["nproc"], capture_output=True, text=True, timeout=2).stdout.strip())
                    load_1_f = float(load_1)
                    if load_1_f > nproc * 0.8:
                        bottlenecks.append({
                            "type": "CPU Load",
                            "severity": "HIGH",
                            "message": f"Load average {load_1_f} approaching CPU count {nproc}",
                            "recommendation": "Check for runaway processes or scale resources"
                        })
                except:
                    pass
            
            # Check I/O
            print("\n  I/O Performance:")
            result = subprocess.run(
                ["iostat", "-x", "1", "2"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[-5:]:
                    if 'sda' in line or 'nvme' in line:
                        print(f"    {line[:80]}")
                        # Check util percentage
                        if '%util' in result.stdout:
                            util = re.findall(r'(\d+\.\d+)%', line)
                            if util and float(util[-1]) > 80:
                                bottlenecks.append({
                                    "type": "Disk I/O",
                                    "severity": "HIGH",
                                    "message": f"Disk utilization at {util[-1]}%",
                                    "recommendation": "Consider faster storage or optimize I/O patterns"
                                })
            
            # Memory pressure
            print("\n  Memory Pressure:")
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                memory_info = lines[1].split()
                total = memory_info[1]
                used = memory_info[2]
                print(f"    Total: {total}, Used: {used}")
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return bottlenecks
    
    def generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        recommendations = []
        
        print("\n🎯 OPTIMIZATION RECOMMENDATIONS")
        print("=" * 80)
        
        recommendations.extend([
            {
                "category": "Storage",
                "priority": "HIGH",
                "recommendation": "Move Docker root to NVMe/SSD if not already there",
                "benefit": "30-50% faster image operations"
            },
            {
                "category": "Memory",
                "priority": "HIGH",
                "recommendation": "Enable memory overcommit with caution (vm.overcommit_memory=1)",
                "benefit": "Better memory utilization"
            },
            {
                "category": "Networking",
                "priority": "MEDIUM",
                "recommendation": "Enable TCP Fast Open (tcp_fastopen=3)",
                "benefit": "Faster TCP connection establishment"
            },
            {
                "category": "Filesystem",
                "priority": "MEDIUM",
                "recommendation": "Increase file descriptor limits to 65536",
                "benefit": "Support more concurrent connections"
            },
            {
                "category": "CPU",
                "priority": "MEDIUM",
                "recommendation": "Enable CPU frequency scaling",
                "benefit": "Better power efficiency"
            },
            {
                "category": "Networking",
                "priority": "MEDIUM",
                "recommendation": "Configure TCP window scaling (tcp_window_scaling=1)",
                "benefit": "Better performance on high-latency networks"
            },
            {
                "category": "Docker",
                "priority": "MEDIUM",
                "recommendation": "Enable BuildKit for faster builds",
                "benefit": "2-4x faster image builds"
            },
            {
                "category": "Swarm Preparation",
                "priority": "HIGH",
                "recommendation": "Configure time sync across all ships (NTP/Chrony)",
                "benefit": "Required for distributed tracing and coordination"
            }
        ])
        
        for rec in recommendations:
            print(f"\n  [{rec['priority']}] {rec['category']}")
            print(f"    • {rec['recommendation']}")
            print(f"    • Benefit: {rec['benefit']}")
        
        return recommendations
    
    def run_deep_analysis(self):
        """Run complete deep system analysis"""
        print("\n" + "=" * 80)
        print("🔬 DEEP SYSTEM ANALYSIS - COMPLETE HARDWARE & SOFTWARE INVENTORY")
        print("=" * 80)
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "deep_system_inventory",
            "hardware": self.analyze_hardware_inventory(),
            "docker": self.analyze_docker_configuration(),
            "services": self.analyze_running_services(),
            "network": self.analyze_network_topology(),
            "storage": self.analyze_storage_subsystem(),
            "bottlenecks": self.identify_performance_bottlenecks(),
            "recommendations": self.generate_optimization_recommendations()
        }
        
        # Save analysis
        with open(self.analysis_report, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print("\n" + "=" * 80)
        print("✅ DEEP ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\n📊 Analysis saved to {self.analysis_report}")
        
        return analysis

if __name__ == "__main__":
    analyzer = DeepSystemAnalysis()
    analyzer.run_deep_analysis()
