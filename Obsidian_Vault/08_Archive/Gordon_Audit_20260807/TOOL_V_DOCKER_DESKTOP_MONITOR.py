#!/usr/bin/env python3
"""
TOOL V: Live Docker Desktop Integration Monitor
Monitors your local Docker Desktop right now
No deployment required - runs instantly
"""

import docker
import json
import sys
from datetime import datetime
from pathlib import Path

class DockerDesktopMonitor:
    def __init__(self):
        self.monitor_log = Path("/data/docker_desktop_live.json")
        self.monitor_log.parent.mkdir(exist_ok=True)
        try:
            self.client = docker.from_env()
            self.connected = True
        except Exception as e:
            print(f"❌ Cannot connect to Docker Desktop: {e}")
            self.client = None
            self.connected = False
    
    def get_local_status(self):
        """Get local Docker Desktop status RIGHT NOW"""
        if not self.connected:
            return {"status": "docker_not_running", "error": "Docker Desktop not accessible"}
        
        try:
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "docker_running": True,
                "containers": {},
                "images": {},
                "networks": {},
                "volumes": {}
            }
            
            # Get containers
            for container in self.client.containers.list(all=True):
                status["containers"][container.name] = {
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "created": container.attrs.get("Created", "unknown")
                }
            
            # Get images
            for image in self.client.images.list():
                for tag in image.tags:
                    size_mb = image.attrs["Size"] / 1024 / 1024
                    status["images"][tag] = {
                        "size_mb": round(size_mb, 2),
                        "created": image.attrs["Created"]
                    }
            
            # Get networks
            for network in self.client.networks.list():
                status["networks"][network.name] = {
                    "driver": network.attrs["Driver"],
                    "containers_attached": len(network.attrs["Containers"])
                }
            
            # Get volumes
            for volume in self.client.volumes.list():
                status["volumes"][volume.name] = {
                    "mountpoint": volume.attrs["Mountpoint"]
                }
            
            return status
        except Exception as e:
            return {"error": str(e)}
    
    def print_status(self):
        """Pretty-print status"""
        status = self.get_local_status()
        
        if "error" in status:
            print(f"⚠️  {status['error']}")
            return
        
        print("\n🐋 DOCKER DESKTOP STATUS")
        print("=" * 60)
        print(f"Timestamp: {status['timestamp']}")
        print(f"Docker Running: {'✅ YES' if status['docker_running'] else '❌ NO'}")
        
        print(f"\n📦 Containers ({len(status['containers'])}):")
        for name, info in status['containers'].items():
            print(f"  • {name}: {info['status']}")
        
        print(f"\n🖼️  Images ({len(status['images'])}):")
        for tag, info in list(status['images'].items())[:5]:
            print(f"  • {tag}: {info['size_mb']} MB")
        if len(status['images']) > 5:
            print(f"  ... and {len(status['images']) - 5} more")
        
        print(f"\n🌐 Networks ({len(status['networks'])}):")
        for name, info in status['networks'].items():
            print(f"  • {name}: {info['containers_attached']} containers")
        
        print(f"\n💾 Volumes ({len(status['volumes'])}):")
        for name in list(status['volumes'].keys())[:3]:
            print(f"  • {name}")
        if len(status['volumes']) > 3:
            print(f"  ... and {len(status['volumes']) - 3} more")
        
        print("\n" + "=" * 60)
    
    def export_json(self, output_file=None):
        """Export status as JSON"""
        status = self.get_local_status()
        output = output_file or Path("/data/docker_desktop_snapshot.json")
        output.parent.mkdir(exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"✅ Exported to {output}")
        return output

if __name__ == "__main__":
    monitor = DockerDesktopMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        monitor.export_json()
    else:
        monitor.print_status()
