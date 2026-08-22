#!/usr/bin/env python3
"""
TOOL AD: Baseline Performance Recorder
Record current system baseline NOW - use to detect anomalies later
"""

import docker
import json
import sys
from datetime import datetime
from pathlib import Path

class BaselineRecorder:
    def __init__(self):
        self.baseline_dir = Path("/data/baselines")
        self.baseline_dir.mkdir(exist_ok=True)
        try:
            self.client = docker.from_env()
            self.connected = True
        except Exception as e:
            print(f"❌ Cannot connect to Docker: {e}")
            self.client = None
            self.connected = False
    
    def record_baseline(self):
        """Record current system baseline"""
        if not self.connected:
            print("⚠️  Docker not available. Cannot record baseline.")
            return None
        
        baseline = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": {},
            "containers_baseline": {},
            "images_baseline": {},
            "volumes_baseline": {}
        }
        
        try:
            print("\n📊 RECORDING SYSTEM BASELINE")
            print("=" * 70)
            
            # System info
            print("Gathering system information...", end=" ", flush=True)
            info = self.client.info()
            baseline["system_info"] = {
                "total_memory_gb": round(info.get("MemTotal", 0) / 1024 / 1024 / 1024, 2),
                "total_cpus": info.get("NCPU", 0),
                "docker_version": info.get("ServerVersion", "unknown"),
                "kernel_version": info.get("KernelVersion", "unknown"),
                "os": info.get("OperatingSystem", "unknown")
            }
            print("✅")
            
            # Containers baseline
            print("Capturing container metrics...", end=" ", flush=True)
            containers_count = 0
            for container in self.client.containers.list():
                try:
                    stats = container.stats(stream=False)
                    cpu_percent = self._calculate_cpu_percent(stats)
                    
                    baseline["containers_baseline"][container.name] = {
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                        "memory_usage_mb": round(stats["memory_stats"]["usage"] / 1024 / 1024, 2),
                        "memory_limit_mb": round(stats["memory_stats"]["limit"] / 1024 / 1024, 2),
                        "cpu_usage_percent": cpu_percent,
                        "status": container.status
                    }
                    containers_count += 1
                except:
                    pass
            print(f"✅ ({containers_count} containers)")
            
            # Images baseline
            print("Cataloging images...", end=" ", flush=True)
            images_count = 0
            for image in self.client.images.list():
                for tag in image.tags:
                    baseline["images_baseline"][tag] = {
                        "size_mb": round(image.attrs["Size"] / 1024 / 1024, 2),
                        "created": image.attrs["Created"]
                    }
                    images_count += 1
            print(f"✅ ({images_count} images)")
            
            # Volumes baseline
            print("Recording volumes...", end=" ", flush=True)
            volumes_count = 0
            for volume in self.client.volumes.list():
                baseline["volumes_baseline"][volume.name] = {
                    "mountpoint": volume.attrs["Mountpoint"],
                    "driver": volume.attrs.get("Driver", "local")
                }
                volumes_count += 1
            print(f"✅ ({volumes_count} volumes)")
            
        except Exception as e:
            print(f"\n⚠️  Error recording baseline: {e}")
            return None
        
        # Save baseline
        baseline_file = self.baseline_dir / f"baseline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print("\n" + "=" * 70)
        print("📈 BASELINE SUMMARY")
        print("=" * 70)
        print(f"System Memory: {baseline['system_info'].get('total_memory_gb', 0)} GB")
        print(f"System CPUs: {baseline['system_info'].get('total_cpus', 0)}")
        print(f"Docker Version: {baseline['system_info'].get('docker_version', 'unknown')}")
        print(f"\nRunning Containers: {len(baseline['containers_baseline'])}")
        print(f"Images: {len(baseline['images_baseline'])}")
        print(f"Volumes: {len(baseline['volumes_baseline'])}")
        
        if baseline['containers_baseline']:
            total_memory = sum(c.get('memory_usage_mb', 0) for c in baseline['containers_baseline'].values())
            print(f"\nTotal container memory: {total_memory:.1f} MB")
        
        print(f"\n✅ Baseline saved to {baseline_file}")
        print("\nThis baseline will be used to detect anomalies and performance degradation.")
        
        return baseline
    
    def _calculate_cpu_percent(self, stats):
        """Calculate CPU usage percentage"""
        try:
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                       stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                          stats["precpu_stats"]["system_cpu_usage"]
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
                return round(cpu_percent, 2)
            return 0
        except:
            return 0

if __name__ == "__main__":
    recorder = BaselineRecorder()
    recorder.record_baseline()
