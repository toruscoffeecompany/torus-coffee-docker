#!/usr/bin/env python3
"""
TOOL AQ: Decision Tree Debugger
When something goes wrong, crew doesn't call for help - they follow a decision tree
"Does it start with network? Yes → Check Tailscale. No → Check Docker. Etc."
"""

import json
from pathlib import Path

class DecisionTreeDebugger:
    def __init__(self):
        self.trees_dir = Path("/data/decision_trees")
        self.trees_dir.mkdir(exist_ok=True)
    
    def build_network_tree(self):
        """Decision tree for network problems"""
        return {
            "root": "Can you reach the ship?",
            "yes": {
                "question": "Can you reach it via Tailscale IP?",
                "yes": {
                    "question": "Can Docker API respond on port 2375?",
                    "yes": "✅ Network OK - Problem is in Docker/containers",
                    "no": "Check Docker: sudo systemctl status docker"
                },
                "no": "Restart Tailscale: sudo systemctl restart tailscaled"
            },
            "no": {
                "question": "Can you ping the local IP?",
                "yes": "Tailscale overlay is down - see 'yes/no' path above",
                "no": "Physical network issue - check cables, switches, firewall"
            }
        }
    
    def build_container_tree(self):
        """Decision tree for container problems"""
        return {
            "root": "Is the container running?",
            "yes": {
                "question": "Is it using high memory/CPU?",
                "yes": {
                    "question": "Did it just start growing?",
                    "yes": "Likely memory leak - check logs: docker logs <container>",
                    "no": "Legitimate usage - increase resources if needed"
                },
                "no": {
                    "question": "Is it responding to requests?",
                    "yes": "✅ Container healthy",
                    "no": "Container zombied - restart: docker restart <container>"
                }
            },
            "no": {
                "question": "Why did it stop?",
                "crashed": {
                    "check": "Check logs for errors: docker logs <container>",
                    "action": "Fix error, restart: docker restart <container>"
                },
                "oom": "Out of memory - increase limit: docker update -m 4g <container>",
                "timeout": "Restart policy - check: docker inspect <container>"
            }
        }
    
    def build_deployment_tree(self):
        """Decision tree for deployment problems"""
        return {
            "root": "Did deployment complete?",
            "yes": {
                "question": "Are all 21 tools running?",
                "yes": "✅ Deployment successful",
                "no": {
                    "question": "How many failed?",
                    "all": "Run deployment again: bash deploy_all_tools.sh",
                    "some": {
                        "action": "Find which failed: docker ps",
                        "next": "Check logs of failed tool",
                        "restart": "docker restart <failed_container>"
                    }
                }
            },
            "no": {
                "question": "At what stage did it fail?",
                "extraction": "Re-run: python TOOL_W_MARKDOWN_EXTRACTOR.py",
                "testing": "Re-run: python TOOL_AA_LOCAL_TEST_HARNESS.py",
                "deployment": "Re-run: bash deploy_all_tools.sh"
            }
        }
    
    def build_performance_tree(self):
        """Decision tree for performance problems"""
        return {
            "root": "What's slow?",
            "container": {
                "question": "Is it using all available resources?",
                "yes": {
                    "action": "Increase resource limits",
                    "command": "docker update -m 4g --cpus 2 <container>"
                },
                "no": {
                    "question": "Is the network slow?",
                    "yes": "Check network: python TOOL_AF_NETWORK_VERIFIER.py",
                    "no": "Application code issue - check logs"
                }
            },
            "network": {
                "action": "Run network diagnostics: python TOOL_AF_NETWORK_VERIFIER.py",
                "check_latency": "See if latency >50ms indicates Tailscale issues"
            },
            "disk": {
                "action": "Check disk: python TOOL_AH_FLEET_HEALTH_DIAGNOSTICS.py",
                "if_full": "Clean up: docker system prune -a --volumes"
            }
        }
    
    def interactive_debugger(self):
        """Run interactive decision tree"""
        print("\n🌳 DECISION TREE DEBUGGER")
        print("=" * 80)
        print("\nWhen something goes wrong, follow the decision tree:")
        print("\nAvailable trees:")
        print("  1. Network problems")
        print("  2. Container problems")
        print("  3. Deployment problems")
        print("  4. Performance problems")
        print("\nExample path through Network tree:")
        
        tree = self.build_network_tree()
        self._print_tree(tree, indent=0)
        
        return tree
    
    def _print_tree(self, node, indent=0):
        """Pretty-print decision tree"""
        prefix = "  " * indent
        
        if isinstance(node, dict):
            if "root" in node:
                print(f"{prefix}❓ {node['root']}")
                if "yes" in node:
                    print(f"{prefix}  ✅ YES:")
                    self._print_tree(node["yes"], indent + 2)
                if "no" in node:
                    print(f"{prefix}  ❌ NO:")
                    self._print_tree(node["no"], indent + 2)
            elif "question" in node:
                print(f"{prefix}❓ {node['question']}")
                if "yes" in node:
                    print(f"{prefix}  ✅ YES:")
                    self._print_tree(node["yes"], indent + 2)
                if "no" in node:
                    print(f"{prefix}  ❌ NO:")
                    self._print_tree(node["no"], indent + 2)
            elif "action" in node or "check" in node or "command" in node:
                if "action" in node:
                    print(f"{prefix}→ {node['action']}")
                if "check" in node:
                    print(f"{prefix}→ {node['check']}")
                if "command" in node:
                    print(f"{prefix}  $ {node['command']}")
        else:
            print(f"{prefix}→ {node}")
    
    def save_all_trees(self):
        """Save all decision trees"""
        print("\n🌳 SAVING DECISION TREES")
        print("=" * 80)
        
        trees = {
            "network": self.build_network_tree(),
            "container": self.build_container_tree(),
            "deployment": self.build_deployment_tree(),
            "performance": self.build_performance_tree()
        }
        
        for tree_name, tree_content in trees.items():
            print(f"\nSaving {tree_name} tree...", end=" ", flush=True)
            tree_file = self.trees_dir / f"decision_tree_{tree_name}.json"
            with open(tree_file, 'w') as f:
                json.dump(tree_content, f, indent=2)
            print("✅")
        
        print(f"\n✅ All decision trees saved to {self.trees_dir}")
        print("\nDecision trees available:")
        for tree_name in trees.keys():
            print(f"  • {tree_name}")

if __name__ == "__main__":
    debugger = DecisionTreeDebugger()
    debugger.interactive_debugger()
    debugger.save_all_trees()
