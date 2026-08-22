#!/usr/bin/env python3
"""
TOOL AA: Local Test Harness
Run all 21 tools in sandbox mode, verify they work before fleet deployment
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from datetime import datetime

class LocalTestHarness:
    def __init__(self, tools_dir="./pirate_tools"):
        self.tools_dir = Path(tools_dir)
        self.test_results = Path("/data/local_test_results.json")
        self.test_results.parent.mkdir(exist_ok=True)
    
    def run_tool_test(self, tool_file):
        """Run a single tool in test mode"""
        test = {
            "tool": tool_file.name,
            "started": datetime.utcnow().isoformat(),
            "status": "pending",
            "output": "",
            "error": "",
            "duration_seconds": 0
        }
        
        try:
            start = time.time()
            result = subprocess.run(
                [sys.executable, str(tool_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = time.time() - start
            
            test["status"] = "success" if result.returncode == 0 else "failed"
            test["output"] = result.stdout[:300]
            test["error"] = result.stderr[:300] if result.stderr else ""
            test["duration_seconds"] = round(duration, 2)
            test["return_code"] = result.returncode
            
            return test
        except subprocess.TimeoutExpired:
            test["status"] = "timeout"
            test["error"] = "Tool exceeded 30 second timeout"
            test["duration_seconds"] = 30
            return test
        except Exception as e:
            test["status"] = "error"
            test["error"] = str(e)
            return test
    
    def run_all_tests(self):
        """Test all tools sequentially"""
        print("\n🧪 LOCAL TEST HARNESS")
        print("=" * 70)
        print("Running all tools in sandbox mode...\n")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_type": "sandbox_verification",
            "total_tools": 0,
            "passed": 0,
            "failed": 0,
            "timeout": 0,
            "tools": []
        }
        
        if not self.tools_dir.exists():
            print(f"❌ Tools directory not found: {self.tools_dir}")
            return results
        
        py_files = sorted(self.tools_dir.glob("*.py"))
        
        if not py_files:
            print(f"❌ No tools found in {self.tools_dir}")
            return results
        
        for tool_file in py_files:
            print(f"🔬 Testing {tool_file.name}...", end=" ", flush=True)
            test = self.run_tool_test(tool_file)
            results["tools"].append(test)
            results["total_tools"] += 1
            
            if test["status"] == "success":
                results["passed"] += 1
                print(f"✅ ({test['duration_seconds']}s)")
            elif test["status"] == "timeout":
                results["timeout"] += 1
                print(f"⏱️  TIMEOUT")
            else:
                results["failed"] += 1
                print(f"❌ FAILED")
                if test["error"]:
                    print(f"   └─ {test['error'][:80]}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total: {results['total_tools']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⏱️  Timeout: {results['timeout']}")
        if results['total_tools'] > 0:
            print(f"Pass rate: {(results['passed']/results['total_tools']*100):.1f}%")
        
        results["safe_to_deploy"] = results["failed"] == 0 and results["timeout"] == 0
        print(f"\n🚀 Safe to deploy: {'✅ YES' if results['safe_to_deploy'] else '❌ NO'}")
        
        # Save
        with open(self.test_results, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📋 Results saved to {self.test_results}")
        
        return results

if __name__ == "__main__":
    harness = LocalTestHarness()
    harness.run_all_tests()
