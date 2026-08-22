#!/usr/bin/env python3
"""
TOOL W: Markdown-to-Executable Converter
Extracts Python code from markdown files and creates runnable scripts
This is what Miss Pink will use to deploy all 21 tools
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime

class MarkdownExtractor:
    def __init__(self, inbox_dir="./00_Inbox", output_dir="./pirate_tools"):
        self.inbox_dir = Path(inbox_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.extraction_log = Path("/data/extraction_log.json")
    
    def extract_python_from_md(self, md_file):
        """Extract all Python code blocks from markdown"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {md_file}: {e}")
            return []
        
        # Find all ```python ... ``` blocks
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        return matches
    
    def create_executable_tools(self):
        """Scan ./00_Inbox/ and create all executable tools"""
        created_tools = []
        
        md_files = {
            "PIRATE_CREW_CLI_TOOL.md": "pirate_crew_cli",
            "FLEET_MONITORING_DASHBOARD.md": "fleet_dashboard",
            "ALL_FIVE_TOOLS_COMPLETE.md": "tools_a_to_e",
            "FIVE_MORE_TOOLS_COMPLETE.md": "tools_f_to_j",
            "TOOLS_K_THROUGH_O_COMPLETE.md": "tools_k_to_o",
            "ADVANCED_CROSS_SHIP_TOOLS_P_TO_U.md": "tools_p_to_u"
        }
        
        print("\n🔍 EXTRACTING TOOLS FROM MARKDOWN")
        print("=" * 60)
        
        for md_file, base_name in md_files.items():
            md_path = self.inbox_dir / md_file
            
            if not md_path.exists():
                print(f"⚠️  Not found: {md_path}")
                continue
            
            print(f"\n📄 Processing {md_file}...")
            code_blocks = self.extract_python_from_md(md_path)
            
            if not code_blocks:
                print(f"  ⚠️  No Python code blocks found")
                continue
            
            for i, code in enumerate(code_blocks):
                # Generate filename
                tool_name = f"{base_name}_{i}.py" if len(code_blocks) > 1 else f"{base_name}.py"
                tool_path = self.output_dir / tool_name
                
                # Write executable
                try:
                    with open(tool_path, 'w', encoding='utf-8') as f:
                        f.write("#!/usr/bin/env python3\n")
                        f.write(f"# Extracted from {md_file}\n")
                        f.write(f"# Generated: {datetime.utcnow().isoformat()}\n\n")
                        f.write(code)
                    
                    os.chmod(tool_path, 0o755)
                    created_tools.append(str(tool_path))
                    print(f"  ✅ Created: {tool_path}")
                except Exception as e:
                    print(f"  ❌ Failed to write {tool_name}: {e}")
        
        return created_tools
    
    def verify_extractions(self, tools):
        """Verify all extracted tools are valid Python"""
        import ast
        
        print("\n✔️  VERIFYING EXTRACTIONS")
        print("=" * 60)
        
        valid = 0
        invalid = 0
        
        for tool_path in tools:
            try:
                with open(tool_path, 'r') as f:
                    ast.parse(f.read())
                print(f"  ✅ {Path(tool_path).name}: Valid Python")
                valid += 1
            except SyntaxError as e:
                print(f"  ❌ {Path(tool_path).name}: Syntax error - {e}")
                invalid += 1
            except Exception as e:
                print(f"  ❌ {Path(tool_path).name}: {e}")
                invalid += 1
        
        print(f"\n📊 Summary: {valid} valid, {invalid} invalid")
        return valid, invalid
    
    def generate_manifest(self, tools):
        """Generate manifest of all tools created"""
        manifest = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tools": len(tools),
            "tools": [str(t) for t in tools],
            "output_directory": str(self.output_dir),
            "next_steps": [
                "1. cd to output directory",
                "2. Review tool files",
                "3. Run: python -m py_compile *.py  (to verify all)",
                "4. Deploy with: bash deploy_all_tools.sh"
            ]
        }
        
        manifest_path = self.output_dir / "MANIFEST.json"
        with open(manifest_path, 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
        
        print(f"\n📋 Manifest created: {manifest_path}")
        return manifest

if __name__ == "__main__":
    extractor = MarkdownExtractor()
    tools = extractor.create_executable_tools()
    
    if tools:
        valid, invalid = extractor.verify_extractions(tools)
        manifest = extractor.generate_manifest(tools)
        
        print(f"\n✅ EXTRACTION COMPLETE")
        print(f"   Created: {len(tools)} tools")
        print(f"   Location: {extractor.output_dir}")
        print(f"   Status: {valid} valid, {invalid} invalid")
    else:
        print("\n❌ No tools extracted. Check markdown files in ./00_Inbox/")
