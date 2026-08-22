#!/usr/bin/env python3
"""
Pirate Crew CLI - Fleet Operations Command Tool
Manages all 3 ships: SQUIDSTATION, PINKCADY, STEALTHATTACK
"""

import click
import json
import requests
import subprocess
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

# Fleet configuration
FLEET = {
    "squidstation": {
        "ip": "100.83.247.14",
        "docker_port": 2375,
        "dashboard_port": 8089,
        "type": "flagship"
    },
    "pinkcady": {
        "ip": "100.106.235.103",
        "docker_port": 2375,
        "webhook_port": 8888,
        "alert_port": 4000,
        "type": "operations"
    },
    "stealthattack": {
        "ip": "100.110.238.68",
        "docker_port": 2375,
        "gpu_exporter": 9445,
        "type": "gpu"
    }
}

class FleetClient:
    def __init__(self, ship: str = None):
        self.ship = ship or "pinkcady"  # Default to PINKCADY
        self.config = FLEET.get(self.ship)
        self.docker_api = f"http://{self.config['ip']}:{self.config['docker_port']}"
    
    def get_containers(self, all: bool = False) -> List[Dict]:
        """Get containers from Docker daemon"""
        try:
            url = f"{self.docker_api}/v1.40/containers/json?all={str(all).lower()}"
            resp = requests.get(url, timeout=5)
            return resp.json()
        except Exception as e:
            console.print(f"[red]Error querying {self.ship}: {e}[/red]")
            return []
    
    def get_container_stats(self, container_id: str) -> Dict:
        """Get real-time stats for container"""
        try:
            url = f"{self.docker_api}/v1.40/containers/{container_id}/stats?stream=false"
            resp = requests.get(url, timeout=5)
            return resp.json()
        except Exception as e:
            console.print(f"[red]Error getting stats: {e}[/red]")
            return {}
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """Get container logs"""
        try:
            url = f"{self.docker_api}/v1.40/containers/{container_id}/logs?tail={tail}&stdout=true&stderr=true"
            resp = requests.get(url, timeout=5)
            return resp.text
        except Exception as e:
            return f"Error: {e}"
    
    def restart_container(self, container_id: str) -> bool:
        """Restart a container"""
        try:
            url = f"{self.docker_api}/v1.40/containers/{container_id}/restart"
            resp = requests.post(url, timeout=10)
            return resp.status_code == 204
        except Exception as e:
            console.print(f"[red]Error restarting: {e}[/red]")
            return False
    
    def execute_in_container(self, container_id: str, cmd: str) -> str:
        """Execute command in container"""
        try:
            # Create exec
            url = f"{self.docker_api}/v1.40/containers/{container_id}/exec"
            create_resp = requests.post(
                url,
                json={"Cmd": cmd.split(), "AttachStdout": True, "AttachStderr": True},
                timeout=5
            )
            exec_id = create_resp.json()["Id"]
            
            # Start exec
            start_url = f"{self.docker_api}/v1.40/exec/{exec_id}/start"
            start_resp = requests.post(start_url, timeout=5)
            return start_resp.text
        except Exception as e:
            return f"Error: {e}"

@click.group()
def cli():
    """🏴‍☠️ Pirate Crew CLI - Fleet Operations"""
    pass

@cli.command()
@click.option("--ship", default=None, help="Specific ship (squidstation/pinkcady/stealthattack)")
def status(ship):
    """Check fleet status"""
    if ship:
        ships = [ship]
    else:
        ships = list(FLEET.keys())
    
    table = Table(title="🏴‍☠️ Fleet Status")
    table.add_column("Ship", style="cyan")
    table.add_column("IP", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Reachable", style="magenta")
    table.add_column("Containers", style="blue")
    
    for s in ships:
        config = FLEET[s]
        client = FleetClient(s)
        
        # Check reachability
        try:
            resp = requests.get(f"{client.docker_api}/_ping", timeout=2)
            reachable = "✓" if resp.status_code == 200 else "✗"
        except:
            reachable = "✗"
        
        # Count containers
        containers = client.get_containers(all=False)
        count = len(containers)
        
        table.add_row(s, config["ip"], config["type"], reachable, str(count))
    
    console.print(table)

@cli.command()
@click.option("--ship", default="pinkcady")
@click.option("--all", is_flag=True, help="Show all containers (including stopped)")
def containers(ship, all):
    """List containers on a ship"""
    client = FleetClient(ship)
    containers_list = client.get_containers(all=all)
    
    table = Table(title=f"Containers on {ship}")
    table.add_column("Name", style="cyan")
    table.add_column("Image", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Ports", style="blue")
    
    for c in containers_list:
        name = c["Names"][0].lstrip("/") if c["Names"] else "unknown"
        image = c["Image"]
        status = c["State"]
        ports = ", ".join([p["PublicPort"] for p in c.get("Ports", []) if "PublicPort" in p]) or "none"
        
        table.add_row(name, image, status, str(ports))
    
    console.print(table)

@cli.command()
@click.argument("container")
@click.option("--ship", default="pinkcady")
@click.option("--tail", default=50, help="Number of lines to show")
def logs(container, ship, tail):
    """View container logs"""
    client = FleetClient(ship)
    containers_list = client.get_containers(all=True)
    
    container_id = None
    for c in containers_list:
        if container in c["Names"][0]:
            container_id = c["Id"]
            break
    
    if not container_id:
        console.print(f"[red]Container {container} not found on {ship}[/red]")
        return
    
    logs_text = client.get_container_logs(container_id, tail=tail)
    console.print(logs_text)

@cli.command()
@click.argument("container")
@click.option("--ship", default="pinkcady")
def stats(container, ship):
    """Show container stats (CPU, memory)"""
    client = FleetClient(ship)
    containers_list = client.get_containers(all=True)
    
    container_id = None
    container_name = None
    for c in containers_list:
        if container in c["Names"][0]:
            container_id = c["Id"]
            container_name = c["Names"][0].lstrip("/")
            break
    
    if not container_id:
        console.print(f"[red]Container {container} not found on {ship}[/red]")
        return
    
    stats_data = client.get_container_stats(container_id)
    
    if not stats_data:
        console.print("[red]Could not retrieve stats[/red]")
        return
    
    # Parse stats
    cpu_stats = stats_data.get("cpu_stats", {})
    memory_stats = stats_data.get("memory_stats", {})
    
    cpu_percent = 0.0
    if "cpu_delta" in cpu_stats and "system_cpu_usage" in cpu_stats:
        cpu_delta = cpu_stats["cpu_delta"]
        system_delta = cpu_stats["system_cpu_usage"]
        cpu_percent = (cpu_delta / system_delta) * 100.0
    
    memory_usage = memory_stats.get("usage", 0) / 1024 / 1024  # MB
    memory_limit = memory_stats.get("limit", 0) / 1024 / 1024  # MB
    
    table = Table(title=f"Stats: {container_name}")
    table.add_row("CPU Usage", f"{cpu_percent:.2f}%")
    table.add_row("Memory Usage", f"{memory_usage:.2f} MB / {memory_limit:.2f} MB")
    
    console.print(table)

@cli.command()
@click.argument("container")
@click.option("--ship", default="pinkcady")
def restart(container, ship):
    """Restart a container"""
    client = FleetClient(ship)
    containers_list = client.get_containers(all=True)
    
    container_id = None
    for c in containers_list:
        if container in c["Names"][0]:
            container_id = c["Id"]
            break
    
    if not container_id:
        console.print(f"[red]Container {container} not found on {ship}[/red]")
        return
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Restarting...", total=None)
        success = client.restart_container(container_id)
        progress.update(task, completed=True)
    
    if success:
        console.print(f"[green]✓ {container} restarted[/green]")
    else:
        console.print(f"[red]✗ Failed to restart {container}[/red]")

@cli.command()
@click.option("--ship", default="stealthattack")
def gpu_status(ship):
    """Check GPU status (STEALTHATTACK)"""
    client = FleetClient(ship)
    
    try:
        url = f"http://{FLEET[ship]['ip']}:{FLEET[ship]['gpu_exporter']}/metrics"
        resp = requests.get(url, timeout=5)
        
        # Parse metrics (simplified)
        metrics = resp.text.split("\n")
        gpu_lines = [m for m in metrics if "nvidia_gpu" in m and not m.startswith("#")]
        
        table = Table(title="GPU Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for line in gpu_lines[:10]:  # Show first 10 metrics
            parts = line.split(" ")
            if len(parts) == 2:
                table.add_row(parts[0], parts[1])
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option("--last", default="1h", help="Time period (1h, 24h, 7d)")
def alerts(last):
    """View recent alerts"""
    # Connect to PINKCADY alert-router
    client = FleetClient("pinkcady")
    
    try:
        # Try to read alerts.json from alert-router volume
        url = f"http://100.106.235.103:4000/alerts?period={last}"
        resp = requests.get(url, timeout=5)
        alerts_data = resp.json()
        
        table = Table(title="Recent Alerts")
        table.add_column("Time", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Service", style="green")
        table.add_column("Message", style="blue")
        
        for alert in alerts_data[-20:]:  # Last 20
            table.add_row(
                alert.get("timestamp", "unknown")[:19],
                alert.get("severity", "info"),
                alert.get("service", "unknown"),
                alert.get("message", "")[:50]
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.argument("job_name")
@click.argument("image")
@click.argument("script")
@click.option("--timeout", default=3600, help="Job timeout in seconds")
def job_submit(job_name, image, script, timeout):
    """Submit GPU job to STEALTHATTACK"""
    client = FleetClient("stealthattack")
    
    console.print(f"[cyan]Submitting GPU job: {job_name}[/cyan]")
    
    # Call job submission endpoint (if exists)
    try:
        payload = {
            "job_name": job_name,
            "image": image,
            "script": script,
            "timeout": timeout
        }
        resp = requests.post(
            f"http://100.110.238.68:5000/jobs/submit",
            json=payload,
            timeout=5
        )
        result = resp.json()
        console.print(f"[green]✓ Job submitted: {result.get('job_id')}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    cli()