#!/usr/bin/env python3
"""
Torus Coffee Automation Orchestrator
Runs all automation scripts in sequence with logging and reporting.
"""
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library" / "05_Operations"
SCRIPTS_DIR = AUTOMATION_DIR / "scripts"
LOGS_DIR = AUTOMATION_DIR / "logs"
PYTHON = AUTOMATION_DIR / "venv" / "Scripts" / "python.exe"

# Configure logging
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('orchestrator')


class AutomationOrchestrator:
    """Orchestrates all Torus Coffee automation scripts."""
    
    def __init__(self):
        self.results = {}
        self.python = str(PYTHON)
        self.scripts_dir = str(SCRIPTS_DIR)
    
    def run_script(self, name: str, args: list = None) -> dict:
        """
        Run a Python script and capture output.
        
        Args:
            name: Script name without .py extension
            args: Optional list of arguments
        
        Returns:
            Result dict with status, output, error
        """
        script_path = Path(self.scripts_dir) / f"{name}.py"
        if not script_path.exists():
            return {
                "status": "error",
                "error": f"Script not found: {script_path}",
                "output": ""
            }
        
        cmd = [self.python, str(script_path)] + (args or [])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            if result.returncode == 0:
                logger.info(f"✓ {name}: success")
                return {
                    "status": "success",
                    "output": output,
                    "error": error,
                    "returncode": result.returncode
                }
            else:
                logger.error(f"✗ {name}: failed with return code {result.returncode}")
                return {
                    "status": "error",
                    "output": output,
                    "error": error,
                    "returncode": result.returncode
                }
        
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {name}: timeout after 5 minutes")
            return {
                "status": "timeout",
                "output": "",
                "error": "Script execution timed out after 5 minutes"
            }
        except Exception as e:
            logger.error(f"✗ {name}: exception - {e}")
            return {
                "status": "exception",
                "output": "",
                "error": str(e)
            }
    
    def run_all(self):
        """Run all automation scripts in sequence."""
        logger.info("=" * 60)
        logger.info("STARTING TORUS COFFEE AUTOMATION ORCHESTRATOR")
        logger.info("=" * 60)
        
        # Define automation sequence
        automations = [
            ("buffer_automation", ["status"]),
            ("zapier_automation", ["status"]),
            ("hubspot_crm", ["test"]),
            ("social_media_automation", ["status"]),
            ("inventory_tracker", ["status"]),
            ("daily_ops_automation", ["status"]),
            ("weekly_review_automation", ["status"]),
            ("monthly_review_automation", ["status"]),
        ]
        
        results = []
        
        for script_name, args in automations:
            logger.info(f"\n--- Running {script_name} ---")
            result = self.run_script(script_name, args)
            results.append({
                "script": script_name,
                "result": result
            })
            
            # Log summary
            if result["status"] == "success":
                logger.info(f"✓ {script_name} completed successfully")
            else:
                logger.warning(f"⚠ {script_name} completed with issues: {result.get('error', 'Unknown')}")
        
        # Generate summary report
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results: list):
        """Generate execution report."""
        logger.info("\n" + "=" * 60)
        logger.info("AUTOMATION ORCHESTRATOR REPORT")
        logger.info("=" * 60)
        
        total = len(results)
        success = sum(1 for r in results if r["result"]["status"] == "success")
        failed = total - success
        
        logger.info(f"Total scripts: {total}")
        logger.info(f"Successful: {success}")
        logger.info(f"Failed/Warnings: {failed}")
        logger.info(f"Success rate: {success/total*100:.1f}%" if total > 0 else "N/A")
        
        logger.info("\nDetailed Results:")
        for item in results:
            script = item["script"]
            result = item["result"]
            status_icon = "✓" if result["status"] == "success" else "✗"
            logger.info(f"  {status_icon} {script}: {result['status']}")
            if result.get("error"):
                logger.info(f"      Error: {result['error'][:100]}")
        
        # Save report to file
        report_file = LOGS_DIR / f"orchestrator_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "success": success,
            "failed": failed,
            "results": [
                {
                    "script": r["script"],
                    "status": r["result"]["status"],
                    "output": r["result"].get("output", "")[:500],
                    "error": r["result"].get("error", "")[:500]
                }
                for r in results
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n✓ Report saved to: {report_file}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    orchestrator = AutomationOrchestrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run":
            results = orchestrator.run_all()
            success_count = sum(1 for r in results if r["result"]["status"] == "success")
            total_count = len(results)
            print(f"\n✓ Orchestrator completed: {success_count}/{total_count} scripts successful")
        elif command == "list":
            print("\nAvailable automation scripts:")
            scripts = [
                "buffer_automation",
                "zapier_automation",
                "hubspot_crm",
                "social_media_automation",
                "inventory_tracker",
                "daily_ops_automation",
                "weekly_review_automation",
                "monthly_review_automation",
            ]
            for script in scripts:
                print(f"  - {script}")
        else:
            print(f"Unknown command: {command}")
            print("Usage: automation_orchestrator.py [run|list]")
    else:
        results = orchestrator.run_all()
        success_count = sum(1 for r in results if r["result"]["status"] == "success")
        total_count = len(results)
        print(f"\n✓ Orchestrator completed: {success_count}/{total_count} scripts successful")


if __name__ == "__main__":
    main()
