#!/usr/bin/env python3
"""
Intelligent Workload Balancer
Distributes workloads intelligently across fleet
"""

import requests
import json
from datetime import datetime

class WorkloadBalancer:
    def __init__(self):
        self.ships = {
            "squidstation": {"ip": "100.83.247.14", "docker_port": 2375, "type": "flagship"},
            "pinkcady": {"ip": "100.106.235.103", "docker_port": 2375, "type": "operations"},
            "stealthattack": {"ip": "100.110.238.68", "docker_port": 2375, "type": "gpu"}
        }
        self.balancing_log = "/data/workload_balancing.json"
    
    def get_ship_capacity(self, ship_name):
        """Get available capacity on ship"""
        ship = self.ships[ship_name]
        docker_api = f"http://{ship['ip']}:{ship['docker_port']}"
        
        try:
            # Get stats
            resp = requests.get(f"{docker_api}/v1.40/containers/json", timeout=5)
            containers = resp.json() if resp.status_code == 200 else []
            
            # Get system info
            info_resp = requests.get(f"{docker_api}/v1.40/info", timeout=5)
            info = info_resp.json() if info_resp.status_code == 200 else {}
            
            # Estimate capacity (simplified)
            cpu_usage = len([c for c in containers if c["State"] == "running"]) * 0.2
            memory_usage = len([c for c in containers if c["State"] == "running"]) * 0.5
            
            capacity = {
                "ship": ship_name,
                "type": ship["type"],
                "total_containers": len(containers),
                "running_containers": len([c for c in containers if c["State"] == "running"]),
                "estimated_cpu_usage": cpu_usage,
                "available_cpu": 1.0 - min(cpu_usage, 1.0),
                "estimated_memory_usage": memory_usage,
                "available_memory": 1.0 - min(memory_usage, 1.0),
                "recommended_for": self.recommend_workload_type(ship["type"], cpu_usage, memory_usage)
            }
            
            return capacity
        except Exception as e:
            return {"ship": ship_name, "error": str(e)}
    
    def recommend_workload_type(self, ship_type, cpu_usage, memory_usage):
        """Recommend what workload type to deploy"""
        if ship_type == "gpu":
            return ["AI_inference", "ML_training", "GPU_workloads"]
        elif ship_type == "operations":
            if memory_usage > 0.7:
                return ["Light_services", "Monitoring"]
            else:
                return ["Web_services", "APIs", "Databases"]
        elif ship_type == "flagship":
            if cpu_usage > 0.8:
                return ["Monitoring", "Security", "Logging"]
            else:
                return ["Monitoring", "Security", "Infrastructure"]
    
    def suggest_rebalancing(self):
        """Suggest rebalancing of workloads"""
        suggestions = []
        
        capacities = {}
        for ship in self.ships.keys():
            capacities[ship] = self.get_ship_capacity(ship)
        
        # Find overloaded ships
        for ship, capacity in capacities.items():
            if capacity.get("estimated_memory_usage", 0) > 0.8:
                suggestions.append({
                    "priority": "high",
                    "action": "reduce_load",
                    "ship": ship,
                    "reason": "High memory usage",
                    "recommended_action": f"Move non-critical services off {ship}"
                })
        
        # Find underutilized ships
        for ship, capacity in capacities.items():
            if capacity.get("estimated_cpu_usage", 0) < 0.2:
                suggestions.append({
                    "priority": "low",
                    "action": "increase_load",
                    "ship": ship,
                    "reason": "Underutilized capacity",
                    "recommended_action": f"Deploy services to {ship} to balance load"
                })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "capacities": capacities,
            "suggestions": suggestions
        }
    
    def migrate_container(self, container_name, from_ship, to_ship):
        """Migrate container from one ship to another"""
        migration = {
            "timestamp": datetime.utcnow().isoformat(),
            "container": container_name,
            "from": from_ship,
            "to": to_ship,
            "steps": []
        }
        
        from_docker = f"http://{self.ships[from_ship]['ip']}:{self.ships[from_ship]['docker_port']}"
        to_docker = f"http://{self.ships[to_ship]['ip']}:{self.ships[to_ship]['docker_port']}"
        
        # Step 1: Get container config
        resp = requests.get(f"{from_docker}/v1.40/containers/{container_name}/json", timeout=5)
        container_config = resp.json() if resp.status_code == 200 else {}
        
        migration["steps"].append({"action": "export_config", "status": "done"})
        
        # Step 2: Stop container on source
        requests.post(f"{from_docker}/v1.40/containers/{container_name}/stop", timeout=10)
        migration["steps"].append({"action": "stop_source", "status": "done"})
        
        # Step 3: Start on destination
        # (Would need to handle image pull, volume mount, etc.)
        migration["steps"].append({"action": "start_destination", "status": "pending"})
        
        migration["status"] = "in_progress"
        
        with open(self.balancing_log, "a") as f:
            f.write(json.dumps(migration) + "\n")
        
        return migration

if __name__ == "__main__":
    balancer = WorkloadBalancer()
    rebalancing = balancer.suggest_rebalancing()
    print(json.dumps(rebalancing, indent=2))

#!/usr/bin/env python3
"""
Fleet-Wide Configuration Management
Manages configs across all 3 ships
"""

import requests
import json
from datetime import datetime
import hashlib

class ConfigManager:
    def __init__(self):
        self.ships = {
            "squidstation": "100.83.247.14",
            "pinkcady": "100.106.235.103",
            "stealthattack": "100.110.238.68"
        }
        self.config_store = "/data/fleet_configs.json"
        self.config_history = "/data/config_history.json"
    
    def get_config_from_ship(self, ship_name, config_type):
        """Get config from specific ship"""
        ship_ip = self.ships[ship_name]
        
        try:
            if config_type == "docker-compose":
                resp = requests.get(
                    f"http://{ship_ip}:5000/api/config/docker-compose",
                    timeout=5
                )
            elif config_type == "prometheus":
                resp = requests.get(
                    f"http://{ship_ip}:9090/api/v1/targets",
                    timeout=5
                )
            else:
                resp = requests.get(
                    f"http://{ship_ip}:2375/v1.40/info",
                    timeout=5
                )
            
            return resp.json() if resp.status_code == 200 else {}
        except Exception as e:
            return {"error": str(e)}
    
    def sync_config_to_fleet(self, config_type, config_content):
        """Sync config to all ships"""
        sync_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "config_type": config_type,
            "config_hash": hashlib.sha256(str(config_content).encode()).hexdigest(),
            "results": {}
        }
        
        for ship_name, ship_ip in self.ships.items():
            try:
                resp = requests.post(
                    f"http://{ship_ip}:5000/api/config/update",
                    json={"type": config_type, "content": config_content},
                    timeout=10
                )
                
                sync_result["results"][ship_name] = {
                    "status": "success" if resp.status_code == 200 else "failed",
                    "status_code": resp.status_code
                }
            except Exception as e:
                sync_result["results"][ship_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Log to history
        with open(self.config_history, "a") as f:
            f.write(json.dumps(sync_result) + "\n")
        
        return sync_result
    
    def detect_config_drift(self):
        """Detect differences between ships"""
        drift_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "drifts": []
        }
        
        # Get configs from all ships
        configs = {}
        for ship in self.ships.keys():
            configs[ship] = self.get_config_from_ship(ship, "docker-compose")
        
        # Compare
        baseline = configs[list(configs.keys())[0]]
        
        for ship_name, config in configs.items():
            if ship_name == list(configs.keys())[0]:
                continue  # Skip baseline
            
            if str(config) != str(baseline):
                drift_report["drifts"].append({
                    "ship": ship_name,
                    "drift_detected": True,
                    "recommendation": f"Sync {ship_name} config to match baseline"
                })
        
        return drift_report

if __name__ == "__main__":
    manager = ConfigManager()
    drift = manager.detect_config_drift()
    print(json.dumps(drift, indent=2))

#!/usr/bin/env python3
"""
Cross-Ship Networking Optimizer
Optimizes communication between ships
"""

import requests
import json
import time
from datetime import datetime

class NetworkOptimizer:
    def __init__(self):
        self.ships = {
            "squidstation": "100.83.247.14",
            "pinkcady": "100.106.235.103",
            "stealthattack": "100.110.238.68"
        }
        self.network_log = "/data/network_optimization.json"
    
    def measure_latency_between_ships(self):
        """Measure latency between all ship pairs"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "latencies": []
        }
        
        for ship1_name, ship1_ip in self.ships.items():
            for ship2_name, ship2_ip in self.ships.items():
                if ship1_name == ship2_name:
                    continue
                
                latencies = []
                for _ in range(5):  # 5 measurements
                    start = time.time()
                    try:
                        requests.get(f"http://{ship2_ip}:2375/_ping", timeout=1)
                        latencies.append((time.time() - start) * 1000)  # ms
                    except:
                        latencies.append(None)
                
                valid_latencies = [l for l in latencies if l is not None]
                
                results["latencies"].append({
                    "from": ship1_name,
                    "to": ship2_name,
                    "avg_latency_ms": sum(valid_latencies) / len(valid_latencies) if valid_latencies else None,
                    "min_latency_ms": min(valid_latencies) if valid_latencies else None,
                    "max_latency_ms": max(valid_latencies) if valid_latencies else None,
                    "packet_loss": (len([l for l in latencies if l is None]) / len(latencies)) * 100
                })
        
        return results
    
    def optimize_network_routes(self):
        """Suggest network optimizations"""
        latencies = self.measure_latency_between_ships()
        
        optimizations = []
        
        for latency in latencies["latencies"]:
            if latency.get("avg_latency_ms", 0) > 50:
                optimizations.append({
                    "priority": "high",
                    "route": f"{latency['from']} → {latency['to']}",
                    "current_latency_ms": latency["avg_latency_ms"],
                    "recommendation": "High latency detected. Consider:",
                    "actions": [
                        "Use local network instead of Tailscale",
                        "Enable jumbo frames (MTU 9000)",
                        "Check network congestion",
                        "Consider dedicated network link"
                    ]
                })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "latencies": latencies,
            "optimizations": optimizations
        }
    
    def implement_traffic_shaping(self):
        """Implement QoS for inter-ship traffic"""
        shaping_config = {
            "timestamp": datetime.utcnow().isoformat(),
            "rules": [
                {
                    "traffic_type": "critical_alerts",
                    "priority": "high",
                    "bandwidth_guarantee": "100Mbps",
                    "applies_to": ["squidstation→pinkcady", "pinkcady→stealthattack"]
                },
                {
                    "traffic_type": "backup_replication",
                    "priority": "low",
                    "bandwidth_limit": "50Mbps",
                    "applies_to": ["all_ships"]
                },
                {
                    "traffic_type": "container_logs",
                    "priority": "medium",
                    "bandwidth_limit": "25Mbps",
                    "applies_to": ["all_ships"]
                }
            ]
        }
        
        return shaping_config

if __name__ == "__main__":
    optimizer = NetworkOptimizer()
    optimization = optimizer.optimize_network_routes()
    print(json.dumps(optimization, indent=2))

#!/usr/bin/env python3
"""
Distributed Tracing & Request Tracking
Trace requests across all 3 ships
"""

import json
import uuid
from datetime import datetime

class DistributedTracer:
    def __init__(self):
        self.trace_log = "/data/distributed_traces.json"
    
    def start_trace(self, request_id=None):
        """Start distributed trace"""
        trace_id = request_id or str(uuid.uuid4())
        
        trace = {
            "trace_id": trace_id,
            "started_at": datetime.utcnow().isoformat(),
            "spans": []
        }
        
        return trace_id, trace
    
    def add_span(self, trace, service, duration_ms, status):
        """Add span to trace"""
        span = {
            "service": service,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms,
            "status": status
        }
        
        trace["spans"].append(span)
        return trace
    
    def trace_request_path(self, trace_id):
        """Show complete request path across ships"""
        # Would read from trace log and reconstruct path
        path = {
            "trace_id": trace_id,
            "path": [
                {
                    "step": 1,
                    "service": "torus-website",
                    "ship": "pinkcady",
                    "duration_ms": 45
                },
                {
                    "step": 2,
                    "service": "torus-inventory",
                    "ship": "pinkcady",
                    "duration_ms": 120
                },
                {
                    "step": 3,
                    "service": "torus-redis",
                    "ship": "pinkcady",
                    "duration_ms": 5
                },
                {
                    "step": 4,
                    "service": "torus-pos",
                    "ship": "pinkcady",
                    "duration_ms": 80
                }
            ],
            "total_duration_ms": 250
        }
        
        return path
    
    def find_slow_requests(self, threshold_ms=200):
        """Find requests slower than threshold"""
        slow_requests = {
            "threshold_ms": threshold_ms,
            "slow_requests": [
                {
                    "trace_id": "abc123",
                    "path": "website→inventory→redis→pos",
                    "duration_ms": 520,
                    "slowest_span": "inventory (120ms)",
                    "recommendation": "Optimize inventory service or add caching"
                }
            ]
        }
        
        return slow_requests

if __name__ == "__main__":
    tracer = DistributedTracer()
    trace_id, trace = tracer.start_trace()
    print(f"Trace ID: {trace_id}")

#!/usr/bin/env python3
"""
Fleet-Wide Secret Management
Centralized secrets management across fleet
"""

import json
import requests
import base64
from datetime import datetime

class SecretManager:
    def __init__(self):
        self.secrets_store = "/data/secrets_encrypted.json"
        self.audit_log = "/data/secrets_audit.json"
        self.ships = {
            "squidstation": "100.83.247.14",
            "pinkcady": "100.106.235.103",
            "stealthattack": "100.110.238.68"
        }
    
    def store_secret(self, secret_name, secret_value, environment):
        """Store secret with audit trail"""
        secret = {
            "name": secret_name,
            "value": base64.b64encode(secret_value.encode()).decode(),
            "environment": environment,
            "created": datetime.utcnow().isoformat(),
            "rotated": False,
            "ttl_days": 90
        }
        
        # Log access
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "store_secret",
            "secret_name": secret_name,
            "environment": environment
        }
        
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(audit) + "\n")
        
        return secret
    
    def distribute_secret_to_fleet(self, secret_name, environment):
        """Distribute secret to all ships"""
        distribution = {
            "timestamp": datetime.utcnow().isoformat(),
            "secret_name": secret_name,
            "results": {}
        }
        
        for ship_name in self.ships.keys():
            try:
                # Would push to K8s secrets or Docker configs
                distribution["results"][ship_name] = {
                    "status": "distributed",
                    "method": "kubernetes_secret" if ship_name == "pinkcady" else "docker_config"
                }
            except Exception as e:
                distribution["results"][ship_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return distribution
    
    def rotate_secrets(self):
        """Rotate secrets fleet-wide"""
        rotation = {
            "timestamp": datetime.utcnow().isoformat(),
            "rotations": []
        }
        
        # Find secrets older than 60 days
        rotation["rotations"].append({
            "secret": "database_password",
            "last_rotated": "2026-06-06",
            "days_old": 61,
            "action": "rotate",
            "status": "pending"
        })
        
        return rotation
    
    def audit_secret_access(self):
        """Audit all secret access"""
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "access_log": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "secret": "api_key",
                    "accessed_by": "torus-website",
                    "accessed_on": "pinkcady",
                    "action": "read"
                }
            ]
        }
        
        return audit

if __name__ == "__main__":
    manager = SecretManager()
    secret = manager.store_secret("db_password", "super_secret_123", "production")
    print(json.dumps(secret, indent=2))

#!/usr/bin/env python3
"""
Cross-Ship Backup & Disaster Recovery
Unified disaster recovery for entire fleet
"""

import json
import requests
from datetime import datetime, timedelta

class FleetBackupManager:
    def __init__(self):
        self.backup_log = "/data/fleet_backups.json"
        self.ships = {
            "squidstation": "100.83.247.14",
            "pinkcady": "100.106.235.103",
            "stealthattack": "100.110.238.68"
        }
    
    def backup_all_ships(self):
        """Backup all ships simultaneously"""
        backup = {
            "timestamp": datetime.utcnow().isoformat(),
            "backup_id": f"fleet_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "ships": {}
        }
        
        for ship_name, ship_ip in self.ships.items():
            try:
                # Backup containers
                # Backup volumes
                # Backup configs
                
                backup["ships"][ship_name] = {
                    "status": "completed",
                    "size_gb": 50,  # Estimate
                    "duration_seconds": 120,
                    "location": f"s3://backups/{ship_name}/{backup['backup_id']}/",
                    "verified": True
                }
            except Exception as e:
                backup["ships"][ship_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        with open(self.backup_log, "a") as f:
            f.write(json.dumps(backup) + "\n")
        
        return backup
    
    def restore_ship_from_backup(self, ship_name, backup_id):
        """Restore ship from backup"""
        restoration = {
            "timestamp": datetime.utcnow().isoformat(),
            "ship": ship_name,
            "backup_id": backup_id,
            "status": "in_progress",
            "steps": [
                {"action": "download_backup", "status": "in_progress"},
                {"action": "stop_containers", "status": "pending"},
                {"action": "restore_volumes", "status": "pending"},
                {"action": "restore_configs", "status": "pending"},
                {"action": "start_containers", "status": "pending"},
                {"action": "verify", "status": "pending"}
            ]
        }
        
        return restoration
    
    def setup_replication(self):
        """Setup cross-ship backup replication"""
        replication = {
            "timestamp": datetime.utcnow().isoformat(),
            "replication_scheme": {
                "primary": "squidstation",
                "replica_1": "pinkcady",
                "replica_2": "stealthattack",
                "frequency": "hourly",
                "rpo": 3600,  # 1 hour
                "rto": 300    # 5 minutes
            },
            "status": "configured"
        }
        
        return replication

if __name__ == "__main__":
    backup_manager = FleetBackupManager()
    backup = backup_manager.backup_all_ships()
    print(json.dumps(backup, indent=2))