#!/usr/bin/env python3
"""
TOOL Y: Artifact Validation Checker
Verifies all 21 tool artifacts are syntactically correct Python
"""

import os
import ast
import json
from pathlib import Path
from datetime import datetime

class ArtifactValidator:
    def __init__(self, tools_dir="./pirate_tools"):
        self.tools_dir = Path(tools_dir)
        self.validation_log = Path("/data/artifact_validation.json")
        self.validation_log.parent.mkdir(exist_ok=True)
    
    def validate_python_syntax(self, file_path):
        """Check if Python file has valid syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            return {"valid": True, "errors": []}
        except SyntaxError as e:
            return {"valid": False, "errors": [str(e)]}
        except Exception as e:
            return {"valid": False, "errors": [f"Read error: {str(e)}"]}
    
    def validate_all_tools(self):
        """Validate all tool files"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tools": 0,
            "valid": 0,
            "invalid": 0,
            "tools": {}
        }
        
        if not self.tools_dir.exists():
            print(f"⚠️  Directory not found: {self.tools_dir}")
            return results
        
        print("\n✔️  VALIDATING ARTIFACTS")
        print("=" * 60)
        
        py_files = list(self.tools_dir.glob("*.py"))
        
        if not py_files:
            print(f"⚠️  No Python files found in {self.tools_dir}")
            return results
        
        for tool_file in sorted(py_files):
            results["total_tools"] += 1
            validation = self.validate_python_syntax(str(tool_file))
            
            if validation["valid"]:
                results["valid"] += 1
                print(f"✅ {tool_file.name}")
            else:
                results["invalid"] += 1
                print(f"❌ {tool_file.name}")
                for error in validation["errors"]:
                    print(f"   Error: {error}")
            
            results["tools"][tool_file.name] = validation
        
        return results
    
    def validate_markdown_sources(self, inbox_dir="./00_Inbox"):
        """Validate that all markdown source files exist"""
        inbox_dir = Path(inbox_dir)
        
        required_files = [
            "PIRATE_CREW_CLI_TOOL.md",
            "FLEET_MONITORING_DASHBOARD.md",
            "ALL_FIVE_TOOLS_COMPLETE.md",
            "FIVE_MORE_TOOLS_COMPLETE.md",
            "TOOLS_K_THROUGH_O_COMPLETE.md",
            "ADVANCED_CROSS_SHIP_TOOLS_P_TO_U.md"
        ]
        
        print("\n📄 VALIDATING MARKDOWN SOURCES")
        print("=" * 60)
        
        found = 0
        missing = []
        
        for md_file in required_files:
            path = inbox_dir / md_file
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"✅ {md_file} ({size_kb:.1f} KB)")
                found += 1
            else:
                print(f"❌ {md_file} - MISSING")
                missing.append(md_file)
        
        return {"found": found, "total": len(required_files), "missing": missing}
    
    def generate_validation_report(self):
        """Generate complete validation report"""
        markdown_validation = self.validate_markdown_sources()
        tool_validation = self.validate_all_tools()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "markdown_sources": markdown_validation,
            "extracted_tools": tool_validation,
            "overall_status": "VALID" if tool_validation["invalid"] == 0 else "INVALID",
            "deployment_ready": (markdown_validation["found"] == markdown_validation["total"] and 
                               tool_validation["invalid"] == 0)
        }
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        print(f"Markdown Sources: {markdown_validation['found']}/{markdown_validation['total']} found")
        print(f"Extracted Tools: {tool_validation['valid']} valid, {tool_validation['invalid']} invalid")
        print(f"Overall Status: {report['overall_status']}")
        print(f"Deployment Ready: {'✅ YES' if report['deployment_ready'] else '❌ NO'}")
        
        if markdown_validation["missing"]:
            print(f"\nMissing files:")
            for f in markdown_validation["missing"]:
                print(f"  - {f}")
        
        # Save report
        with open(self.validation_log, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved to {self.validation_log}")
        
        return report

if __name__ == "__main__":
    validator = ArtifactValidator()
    validator.generate_validation_report()
