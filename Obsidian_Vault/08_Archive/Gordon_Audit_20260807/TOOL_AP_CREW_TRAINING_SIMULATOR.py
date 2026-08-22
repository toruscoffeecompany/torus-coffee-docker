#!/usr/bin/env python3
"""
TOOL AP: Crew Training Simulator
Simulate scenarios so crew can practice responses WITHOUT affecting production
"If this happens... what would you do?" with instant feedback
"""

import json
import random
from pathlib import Path
from datetime import datetime

class CrewTrainingSimulator:
    def __init__(self):
        self.scenarios_dir = Path("/data/training_scenarios")
        self.scenarios_dir.mkdir(exist_ok=True)
        self.results_dir = Path("/data/training_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def scenario_memory_spike(self):
        """Scenario: Memory suddenly spikes on PINKCADY"""
        return {
            "scenario_id": "MEM-001",
            "title": "Memory Spike on PINKCADY",
            "difficulty": "BEGINNER",
            "situation": "You receive an alert: PINKCADY memory jumped from 60% to 85% in 5 minutes",
            "questions": [
                {
                    "question": "What's your first action?",
                    "options": [
                        "A) Panic and restart everything",
                        "B) Run health diagnostics to understand the situation",
                        "C) Kill the largest container immediately",
                        "D) Call someone else"
                    ],
                    "correct_answer": "B",
                    "explanation": "Always understand the situation first. Running diagnostics gives you data to make good decisions."
                },
                {
                    "question": "You see a container using 3.5GB of the 6.8GB available. What does that tell you?",
                    "options": [
                        "A) The container has a memory leak",
                        "B) The container might have a memory leak OR is just legitimately memory-hungry",
                        "C) You should restart it immediately",
                        "D) The application is broken"
                    ],
                    "correct_answer": "B",
                    "explanation": "High memory doesn't always mean a leak. It could be legitimate usage. Monitor trends to confirm."
                },
                {
                    "question": "If memory continues climbing, what should you do?",
                    "options": [
                        "A) Restart the container",
                        "B) Increase memory limit",
                        "C) Check container logs for errors",
                        "D) All of the above (restart to test, if it happens again increase limit)"
                    ],
                    "correct_answer": "D",
                    "explanation": "Methodical approach: test hypothesis (restart), if it repeats, investigate (logs), then remediate (increase limit)"
                }
            ],
            "learning_points": [
                "Always diagnose before acting",
                "Distinguish between spikes and trends",
                "Use data to make decisions",
                "Document what you tried"
            ]
        }
    
    def scenario_network_down(self):
        """Scenario: STEALTHATTACK can't reach PINKCADY"""
        return {
            "scenario_id": "NET-001",
            "title": "Network Connectivity Lost",
            "difficulty": "INTERMEDIATE",
            "situation": "STEALTHATTACK reporting connection refused when trying to reach PINKCADY's Docker API",
            "questions": [
                {
                    "question": "First diagnostic step?",
                    "options": [
                        "A) Restart Docker on both ships",
                        "B) Check if PINKCADY is responding to ping",
                        "C) Assume network is down",
                        "D) Restart Tailscale"
                    ],
                    "correct_answer": "B",
                    "explanation": "Ping tells you if the host is reachable. If ping works, Docker issue. If not, network issue."
                },
                {
                    "question": "Ping fails. Next step?",
                    "options": [
                        "A) Restart PINKCADY",
                        "B) Check Tailscale status",
                        "C) Assume hardware failure",
                        "D) Wait for it to come back online"
                    ],
                    "correct_answer": "B",
                    "explanation": "Tailscale is the overlay network. If it's not running or disconnected, connectivity fails."
                }
            ],
            "learning_points": [
                "Network troubleshooting is methodical: ping → resolve → verify",
                "Overlay networks (Tailscale) can fail independently of physical network",
                "Always verify basics before complex solutions"
            ]
        }
    
    def scenario_deployment_fails(self):
        """Scenario: Deployment of 21 tools partially fails"""
        return {
            "scenario_id": "DEP-001",
            "title": "Deployment Partial Failure",
            "difficulty": "ADVANCED",
            "situation": "Deployed 21 tools, but 3 failed to start. You need to get them running ASAP.",
            "questions": [
                {
                    "question": "How do you identify which 3 failed?",
                    "options": [
                        "A) Run TOOL_AB_DEPLOYMENT_VERIFIER.py to see status",
                        "B) Check docker ps manually",
                        "C) Look at logs for each tool",
                        "D) All of above"
                    ],
                    "correct_answer": "D",
                    "explanation": "Use verification tool for overview, manual check for specifics, logs for details."
                },
                {
                    "question": "Two tools failed due to port conflicts (ports already in use). What's the fix?",
                    "options": [
                        "A) Kill the process using the port",
                        "B) Change the port number in the tool config",
                        "C) Restart the tools with -p flag",
                        "D) Restart Docker"
                    ],
                    "correct_answer": "A",
                    "explanation": "Identify what's using the port (lsof), stop that process, then restart tools."
                }
            ],
            "learning_points": [
                "Partial failures happen - have a plan to deal with them",
                "Verification tools are your friend",
                "Port conflicts are common - know how to resolve them",
                "Always check logs last (they confirm your diagnosis)"
            ]
        }
    
    def run_training_session(self, scenario_id):
        """Run an interactive training scenario"""
        print("\n🎓 CREW TRAINING SIMULATOR")
        print("=" * 80)
        
        scenarios = {
            "MEM-001": self.scenario_memory_spike(),
            "NET-001": self.scenario_network_down(),
            "DEP-001": self.scenario_deployment_fails()
        }
        
        scenario = scenarios.get(scenario_id)
        if not scenario:
            print(f"Scenario {scenario_id} not found")
            return
        
        print(f"\n📚 Scenario: {scenario['title']}")
        print(f"Difficulty: {scenario['difficulty']}")
        print(f"\n📋 SITUATION:\n{scenario['situation']}\n")
        
        score = 0
        total_questions = len(scenario['questions'])
        
        for idx, q in enumerate(scenario['questions'], 1):
            print(f"\n❓ Question {idx}/{total_questions}:")
            print(q['question'])
            print()
            
            for option in q['options']:
                print(f"  {option}")
            
            # In interactive mode, would get user input
            # For now, simulate correct answer
            user_answer = q['correct_answer']
            
            if user_answer == q['correct_answer']:
                print(f"\n✅ CORRECT!")
                score += 1
            else:
                print(f"\n❌ INCORRECT - Correct answer was {q['correct_answer']}")
            
            print(f"💡 {q['explanation']}")
        
        # Generate result
        result = {
            "training_session": datetime.utcnow().isoformat(),
            "scenario_id": scenario_id,
            "scenario_title": scenario['title'],
            "score": f"{score}/{total_questions}",
            "percentage": f"{(score/total_questions)*100:.0f}%",
            "learning_points": scenario['learning_points']
        }
        
        print(f"\n" + "=" * 80)
        print(f"📊 RESULT: {result['score']} ({result['percentage']})")
        print(f"\n📚 Key Learnings:")
        for point in scenario['learning_points']:
            print(f"  • {point}")
        
        # Save result
        result_file = self.results_dir / f"training_{scenario_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n✅ Result saved to {result_file}")
        
        return result
    
    def list_scenarios(self):
        """List all available training scenarios"""
        print("\n🎓 AVAILABLE TRAINING SCENARIOS")
        print("=" * 80)
        
        scenarios = [
            ("MEM-001", "Memory Spike", "BEGINNER"),
            ("NET-001", "Network Down", "INTERMEDIATE"),
            ("DEP-001", "Deployment Fails", "ADVANCED")
        ]
        
        for scenario_id, title, difficulty in scenarios:
            print(f"\n{scenario_id}: {title}")
            print(f"  Difficulty: {difficulty}")
            print(f"  Run: python TOOL_AP_CREW_TRAINING.py {scenario_id}")

if __name__ == "__main__":
    import sys
    simulator = CrewTrainingSimulator()
    
    if len(sys.argv) > 1:
        scenario_id = sys.argv[1]
        simulator.run_training_session(scenario_id)
    else:
        simulator.list_scenarios()
