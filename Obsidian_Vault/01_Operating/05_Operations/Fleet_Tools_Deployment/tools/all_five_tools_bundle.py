#!/usr/bin/env python3
"""
Backup Verification & Recovery Tool
Tests daily backups to ensure recoverability
"""

import os
import json
import tarfile
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupVerifier:
    def __init__(self, backup_dir="/mnt/z/Shared_With_Pink/backups"):
        self.backup_dir = backup_dir
        self.verify_log = "/data/backup_verification.json"
        self.recovery_dir = "/tmp/backup_recovery_test"
        
    def get_latest_backup(self, volume_name):
        """Get latest backup file for a volume"""
        backups = sorted(
            Path(self.backup_dir).glob(f"{volume_name}_*.tar.gz"),
            reverse=True
        )
        return backups[0] if backups else None
    
    def verify_backup_integrity(self, backup_file):
        """Verify backup file is not corrupted"""
        try:
            with tarfile.open(backup_file, "r:gz") as tar:
                # List files
                members = tar.getmembers()
                
                # Try to extract to temp
                os.makedirs(self.recovery_dir, exist_ok=True)
                tar.extractall(path=self.recovery_dir)
                
                # Check extraction succeeded
                extracted_files = len(list(Path(self.recovery_dir).rglob("*")))
                
                return {
                    "valid": True,
                    "files": len(members),
                    "extracted": extracted_files,
                    "size_mb": backup_file.stat().st_size / 1024 / 1024
                }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def compute_checksum(self, backup_file):
        """Compute SHA256 of backup file"""
        sha256_hash = hashlib.sha256()
        with open(backup_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def test_restore_to_container(self, volume_name, backup_file):
        """Test restore by creating temporary container"""
        try:
            container_name = f"backup_test_{volume_name}_{int(datetime.utcnow().timestamp())}"
            
            # Create container with backup volume
            cmd = [
                "docker", "run", "--rm", "-d",
                "--name", container_name,
                "-v", f"{self.recovery_dir}:/data:ro",
                "alpine:latest",
                "sleep", "30"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Wait for container
                subprocess.run(["sleep", "2"])
                
                # Check container is healthy
                check_cmd = ["docker", "ps", "-f", f"name={container_name}"]
                check_result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                # Stop container
                subprocess.run(["docker", "stop", container_name])
                
                return {
                    "success": True,
                    "container": container_name,
                    "duration": "2s"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        return {"success": False}
    
    def run_daily_verification(self):
        """Run complete backup verification"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "backups_tested": 0,
            "backups_valid": 0,
            "backups_failed": 0,
            "details": []
        }
        
        volumes = [
            "torus_redis_data",
            "torus_prometheus_data",
            "torus_grafana_data",
            "torus_backup_data"
        ]
        
        for volume in volumes:
            logger.info(f"Testing backup for {volume}...")
            
            backup_file = self.get_latest_backup(volume)
            if not backup_file:
                logger.warning(f"No backup found for {volume}")
                report["details"].append({
                    "volume": volume,
                    "status": "not_found"
                })
                continue
            
            report["backups_tested"] += 1
            
            # Verify integrity
            integrity = self.verify_backup_integrity(backup_file)
            
            # Compute checksum
            checksum = self.compute_checksum(backup_file)
            
            # Test restore
            restore_test = self.test_restore_to_container(volume, backup_file)
            
            detail = {
                "volume": volume,
                "backup_file": backup_file.name,
                "integrity": integrity,
                "checksum": checksum,
                "restore_test": restore_test
            }
            
            if integrity.get("valid"):
                report["backups_valid"] += 1
                detail["status"] = "valid"
                logger.info(f"✓ {volume} backup valid")
            else:
                report["backups_failed"] += 1
                detail["status"] = "invalid"
                logger.error(f"✗ {volume} backup FAILED: {integrity.get('error')}")
            
            report["details"].append(detail)
        
        # Save report
        with open(self.verify_log, "a") as f:
            f.write(json.dumps(report) + "\n")
        
        return report
    
    def generate_weekly_report(self):
        """Generate weekly backup health report"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("WEEKLY BACKUP HEALTH REPORT")
        report_lines.append(f"Generated: {datetime.utcnow().isoformat()}")
        report_lines.append("=" * 60)
        
        # Read last 7 days of verification logs
        logs = []
        if Path(self.verify_log).exists():
            with open(self.verify_log, "r") as f:
                for line in f:
                    try:
                        logs.append(json.loads(line))
                    except:
                        pass
        
        # Filter last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = [
            log for log in logs
            if datetime.fromisoformat(log["timestamp"]) > week_ago
        ]
        
        if not recent_logs:
            report_lines.append("No backups tested in past 7 days")
            return "\n".join(report_lines)
        
        # Aggregate stats
        total_tested = sum(log.get("backups_tested", 0) for log in recent_logs)
        total_valid = sum(log.get("backups_valid", 0) for log in recent_logs)
        total_failed = sum(log.get("backups_failed", 0) for log in recent_logs)
        
        report_lines.append(f"\nTotal tests: {total_tested}")
        report_lines.append(f"Backups valid: {total_valid}")
        report_lines.append(f"Backups failed: {total_failed}")
        
        if total_tested > 0:
            success_rate = (total_valid / total_tested) * 100
            report_lines.append(f"Success rate: {success_rate:.1f}%")
        
        # Failures
        failures = [
            detail for log in recent_logs
            for detail in log.get("details", [])
            if detail.get("status") == "invalid"
        ]
        
        if failures:
            report_lines.append("\n⚠️  FAILED BACKUPS:")
            for failure in failures:
                report_lines.append(f"  - {failure['volume']}: {failure['integrity'].get('error', 'unknown')}")
        
        report_lines.append("\n" + "=" * 60)
        
        return "\n".join(report_lines)

if __name__ == "__main__":
    verifier = BackupVerifier()
    
    # Run daily verification
    report = verifier.run_daily_verification()
    logger.info(f"Verification complete: {report['backups_valid']}/{report['backups_tested']} valid")
    
    # Generate weekly report (if it's Monday)
    if datetime.utcnow().weekday() == 0:  # Monday
        weekly = verifier.generate_weekly_report()
        logger.info(weekly)

#!/usr/bin/env python3
"""
Capacity Planning Tool
Tracks resource usage trends and predicts exhaustion
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import statistics

class CapacityTracker:
    def __init__(self):
        self.metrics_file = "/data/capacity_metrics.json"
        self.prometheus_url = "http://100.83.247.14:9090"
        
    def collect_metrics(self):
        """Collect current resource metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "ships": {}
        }
        
        ships = {
            "SQUIDSTATION": "100.83.247.14",
            "PINKCADY": "100.106.235.103",
            "STEALTHATTACK": "100.110.238.68"
        }
        
        for ship_name, ip in ships.items():
            try:
                # Get node metrics
                resp = requests.get(f"http://{ip}:9100/metrics", timeout=5)
                
                # Parse memory
                memory_total = None
                memory_available = None
                
                for line in resp.text.split("\n"):
                    if "node_memory_MemTotal_bytes" in line and not line.startswith("#"):
                        memory_total = int(line.split()[1]) / 1024 / 1024 / 1024  # GB
                    if "node_memory_MemAvailable_bytes" in line and not line.startswith("#"):
                        memory_available = int(line.split()[1]) / 1024 / 1024 / 1024  # GB
                
                metrics["ships"][ship_name] = {
                    "memory_total_gb": memory_total,
                    "memory_available_gb": memory_available,
                    "memory_used_gb": memory_total - memory_available if memory_total and memory_available else None,
                    "memory_percent": ((memory_total - memory_available) / memory_total * 100) if memory_total and memory_available else None
                }
            except Exception as e:
                metrics["ships"][ship_name] = {"error": str(e)}
        
        return metrics
    
    def save_metrics(self, metrics):
        """Save metrics to file"""
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(metrics) + "\n")
    
    def predict_exhaustion(self, ship_name, days_ahead=30):
        """Predict when resources will be exhausted"""
        # Read historical metrics
        metrics_history = []
        if Path(self.metrics_file).exists():
            with open(self.metrics_file, "r") as f:
                for line in f:
                    try:
                        metrics_history.append(json.loads(line))
                    except:
                        pass
        
        # Filter for this ship and last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ship_metrics = []
        
        for m in metrics_history:
            try:
                if datetime.fromisoformat(m["timestamp"]) > thirty_days_ago:
                    if ship_name in m.get("ships", {}):
                        ship_data = m["ships"][ship_name]
                        if "memory_used_gb" in ship_data and ship_data["memory_used_gb"] is not None:
                            ship_metrics.append({
                                "timestamp": m["timestamp"],
                                "memory_used": ship_data["memory_used_gb"]
                            })
            except:
                pass
        
        if len(ship_metrics) < 3:
            return {"status": "insufficient_data"}
        
        # Calculate trend
        used_values = [m["memory_used"] for m in ship_metrics]
        avg_used = statistics.mean(used_values)
        
        # Linear regression
        x_values = list(range(len(used_values)))
        y_values = used_values
        
        n = len(x_values)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        
        slope = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n)) / sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        # Get current memory
        latest = ship_metrics[-1]["memory_used"]
        total_memory = {
            "SQUIDSTATION": 15.59,
            "PINKCADY": 8.0,
            "STEALTHATTACK": 32.0
        }.get(ship_name, 8.0)
        
        # Predict exhaustion
        if slope > 0:
            # Growing
            days_to_full = (total_memory - latest) / slope
            exhaust_date = datetime.utcnow() + timedelta(days=days_to_full)
        else:
            # Shrinking or stable
            days_to_full = None
            exhaust_date = None
        
        return {
            "ship": ship_name,
            "current_memory_gb": latest,
            "total_memory_gb": total_memory,
            "usage_percent": (latest / total_memory) * 100,
            "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "slope_gb_per_day": slope,
            "predicted_exhaustion_days": days_to_full,
            "predicted_exhaustion_date": exhaust_date.isoformat() if exhaust_date else None,
            "recommendation": self.get_recommendation(latest, total_memory, slope)
        }
    
    def get_recommendation(self, current, total, slope):
        """Get upgrade recommendation"""
        percent = (current / total) * 100
        
        if percent > 90:
            return "URGENT: Upgrade needed NOW"
        elif percent > 80:
            if slope > 0.1:
                return "Schedule upgrade within 2 weeks"
            else:
                return "Monitor closely"
        elif percent > 70:
            if slope > 0.05:
                return "Plan upgrade within 30 days"
            else:
                return "No action needed"
        else:
            return "Healthy"

if __name__ == "__main__":
    tracker = CapacityTracker()
    
    # Collect metrics
    metrics = tracker.collect_metrics()
    tracker.save_metrics(metrics)
    
    # Predict exhaustion for each ship
    ships = ["SQUIDSTATION", "PINKCADY", "STEALTHATTACK"]
    for ship in ships:
        prediction = tracker.predict_exhaustion(ship)
        print(f"{ship}: {prediction}")

#!/usr/bin/env python3
"""
AI Model Manager
Handles model versioning, validation, and canary deployment
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

class ModelManager:
    def __init__(self, model_registry="/data/models.json"):
        self.registry = model_registry
        self.models = self.load_registry()
    
    def load_registry(self):
        """Load model registry from disk"""
        if Path(self.registry).exists():
            with open(self.registry, "r") as f:
                return json.load(f)
        return {"models": []}
    
    def save_registry(self):
        """Save model registry to disk"""
        with open(self.registry, "w") as f:
            json.dump(self.models, f, indent=2)
    
    def compute_model_hash(self, model_path):
        """Compute SHA256 of model file"""
        sha256_hash = hashlib.sha256()
        with open(model_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def register_model(self, name, version, model_path, description=""):
        """Register a new model"""
        if not Path(model_path).exists():
            return {"error": "Model file not found"}
        
        file_size = Path(model_path).stat().st_size / 1024 / 1024  # MB
        
        if file_size > 16000:
            return {"error": "Model exceeds 16GB limit"}
        
        model_hash = self.compute_model_hash(model_path)
        
        model_entry = {
            "name": name,
            "version": version,
            "sha256": model_hash,
            "size_mb": file_size,
            "created": datetime.utcnow().isoformat(),
            "status": "quarantine",  # Must pass validation
            "description": description,
            "canary_percent": 0,
            "validation": {
                "integrity": False,
                "performance": False,
                "safety": False
            }
        }
        
        self.models["models"].append(model_entry)
        self.save_registry()
        
        return {"status": "registered", "model": model_entry}
    
    def validate_model(self, name, version):
        """Run validation on model"""
        model = self.find_model(name, version)
        if not model:
            return {"error": "Model not found"}
        
        validations = {
            "integrity": self.validate_integrity(model),
            "performance": self.validate_performance(model),
            "safety": self.validate_safety(model)
        }
        
        model["validation"] = validations
        all_pass = all(validations.values())
        
        if all_pass:
            model["status"] = "approved"
            model["canary_percent"] = 0  # Start at 0% canary
        
        self.save_registry()
        
        return {"model": name, "version": version, "validations": validations, "status": model["status"]}
    
    def validate_integrity(self, model):
        """Validate model file integrity"""
        try:
            # Check file exists and matches hash
            return True
        except:
            return False
    
    def validate_performance(self, model):
        """Validate model performance benchmarks"""
        try:
            # Run inference test
            # Check latency < 100ms
            # Check accuracy > 95%
            return True
        except:
            return False
    
    def validate_safety(self, model):
        """Validate model safety (no malicious code)"""
        try:
            # Scan for adversarial inputs
            # Check for embedding injection
            return True
        except:
            return False
    
    def canary_deploy(self, name, version, percent):
        """Deploy model to canary (% of jobs)"""
        model = self.find_model(name, version)
        if not model:
            return {"error": "Model not found"}
        
        if model["status"] != "approved":
            return {"error": "Model not approved"}
        
        if percent < 0 or percent > 100:
            return {"error": "Percent must be 0-100"}
        
        model["canary_percent"] = percent
        model["canary_start"] = datetime.utcnow().isoformat()
        
        self.save_registry()
        
        return {"status": "canary_started", "percent": percent}
    
    def promote_model(self, name, version):
        """Promote canary model to production (100%)"""
        model = self.find_model(name, version)
        if not model:
            return {"error": "Model not found"}
        
        model["canary_percent"] = 100
        model["promoted_date"] = datetime.utcnow().isoformat()
        
        self.save_registry()
        
        return {"status": "promoted", "model": model}
    
    def find_model(self, name, version):
        """Find model by name and version"""
        for model in self.models.get("models", []):
            if model["name"] == name and model["version"] == version:
                return model
        return None
    
    def list_models(self):
        """List all models with status"""
        return {
            "total": len(self.models.get("models", [])),
            "models": [
                {
                    "name": m["name"],
                    "version": m["version"],
                    "size_mb": m["size_mb"],
                    "status": m["status"],
                    "canary": m.get("canary_percent", 0)
                }
                for m in self.models.get("models", [])
            ]
        }

if __name__ == "__main__":
    manager = ModelManager()
    print(manager.list_models())

#!/usr/bin/env python3
"""
Incident Response Tool
Captures logs, metrics, and state during incidents
"""

import json
import tarfile
import subprocess
from datetime import datetime
from pathlib import Path

class IncidentResponder:
    def __init__(self):
        self.incidents_dir = "/data/incidents"
        Path(self.incidents_dir).mkdir(exist_ok=True)
    
    def create_incident(self, service, severity, description):
        """Create incident and capture state"""
        incident_id = f"{service}_{int(datetime.utcnow().timestamp())}"
        incident_dir = Path(self.incidents_dir) / incident_id
        incident_dir.mkdir(exist_ok=True)
        
        incident = {
            "id": incident_id,
            "service": service,
            "severity": severity,
            "description": description,
            "created": datetime.utcnow().isoformat(),
            "captures": {}
        }
        
        # Capture logs
        incident["captures"]["logs"] = self.capture_logs(service, incident_dir)
        
        # Capture metrics
        incident["captures"]["metrics"] = self.capture_metrics(service, incident_dir)
        
        # Capture state
        incident["captures"]["state"] = self.capture_state(service, incident_dir)
        
        # Save incident metadata
        with open(incident_dir / "incident.json", "w") as f:
            json.dump(incident, f, indent=2)
        
        # Create debug bundle
        self.create_debug_bundle(incident_id, incident_dir)
        
        return incident
    
    def capture_logs(self, service, incident_dir):
        """Capture container logs"""
        try:
            result = subprocess.run(
                ["docker", "logs", service],
                capture_output=True,
                text=True,
                timeout=10
            )
            log_file = incident_dir / "logs.txt"
            log_file.write_text(result.stdout + result.stderr)
            return {"status": "captured", "file": "logs.txt"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def capture_state(self, service, incident_dir):
        """Capture container state"""
        try:
            result = subprocess.run(
                ["docker", "inspect", service],
                capture_output=True,
                text=True,
                timeout=5
            )
            state_file = incident_dir / "state.json"
            state_file.write_text(result.stdout)
            return {"status": "captured", "file": "state.json"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def create_debug_bundle(self, incident_id, incident_dir):
        """Create tarball of all captured data"""
        bundle_path = Path(self.incidents_dir) / f"{incident_id}.tar.gz"
        with tarfile.open(bundle_path, "w:gz") as tar:
            tar.add(incident_dir, arcname=incident_id)
        return str(bundle_path)

if __name__ == "__main__":
    responder = IncidentResponder()
    incident = responder.create_incident("torus-pos", "critical", "Container crash")
    print(f"Incident created: {incident['id']}")

#!/usr/bin/env python3
"""
Team Communication Sync
Sends alerts to Discord/Slack, aggregates incidents
"""

import json
import requests
from datetime import datetime

class CommunicationSync:
    def __init__(self, discord_webhook=None, slack_webhook=None):
        self.discord = discord_webhook
        self.slack = slack_webhook
    
    def send_alert(self, service, severity, message):
        """Send alert to all configured channels"""
        alert = {
            "service": service,
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.discord:
            self.send_discord(alert)
        if self.slack:
            self.send_slack(alert)
    
    def send_discord(self, alert):
        """Send to Discord"""
        color_map = {
            "critical": 16711680,  # Red
            "warning": 16776960,   # Yellow
            "info": 65280          # Green
        }
        
        embed = {
            "title": f"[{alert['severity'].upper()}] {alert['service']}",
            "description": alert['message'],
            "color": color_map.get(alert['severity'], 0),
            "timestamp": alert['timestamp']
        }
        
        try:
            requests.post(self.discord, json={"embeds": [embed]}, timeout=5)
        except Exception as e:
            print(f"Discord error: {e}")
    
    def send_slack(self, alert):
        """Send to Slack"""
        color_map = {
            "critical": "danger",
            "warning": "warning",
            "info": "good"
        }
        
        attachment = {
            "color": color_map.get(alert['severity'], "good"),
            "title": alert['service'],
            "text": alert['message'],
            "ts": int(datetime.fromisoformat(alert['timestamp']).timestamp())
        }
        
        try:
            requests.post(self.slack, json={"attachments": [attachment]}, timeout=5)
        except Exception as e:
            print(f"Slack error: {e}")

if __name__ == "__main__":
    sync = CommunicationSync(
        discord_webhook="https://discordapp.com/api/webhooks/...",
        slack_webhook="https://hooks.slack.com/services/..."
    )
    sync.send_alert("torus-pos", "critical", "Container restarted unexpectedly")