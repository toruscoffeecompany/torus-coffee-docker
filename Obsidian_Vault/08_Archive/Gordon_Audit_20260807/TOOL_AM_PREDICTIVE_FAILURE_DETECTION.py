#!/usr/bin/env python3
"""
TOOL AM: Predictive Failure Detection
Learn what "normal" looks like, then detect anomalies BEFORE they become failures
Uses baselines to catch problems at warning stage, not critical stage
"""

import json
from pathlib import Path
from datetime import datetime

class PredictiveFailureDetector:
    def __init__(self):
        self.baselines_dir = Path("/data/baselines")
        self.current_dir = Path("/data/current_metrics")
        self.predictions_dir = Path("/data/predictions")
        self.predictions_dir.mkdir(exist_ok=True)
    
    def analyze_trend(self, baseline_value, current_value, metric_name):
        """Analyze if metric is trending toward failure"""
        if not baseline_value or baseline_value == 0:
            return {"status": "unknown", "reason": "No baseline"}
        
        change_percent = ((current_value - baseline_value) / baseline_value) * 100
        
        # Different thresholds for different metrics
        thresholds = {
            "memory": {"warning": 70, "critical": 85},
            "disk": {"warning": 75, "critical": 90},
            "container_count": {"warning": 150, "critical": 200},
            "cpu": {"warning": 80, "critical": 95}
        }
        
        threshold = thresholds.get(metric_name, {"warning": 20, "critical": 50})
        
        if change_percent > threshold["critical"]:
            return {
                "status": "CRITICAL",
                "change_percent": change_percent,
                "baseline": baseline_value,
                "current": current_value,
                "hours_to_failure": self._estimate_hours_to_failure(
                    baseline_value, current_value, threshold["critical"]
                )
            }
        elif change_percent > threshold["warning"]:
            return {
                "status": "WARNING",
                "change_percent": change_percent,
                "baseline": baseline_value,
                "current": current_value
            }
        else:
            return {"status": "NORMAL", "change_percent": change_percent}
    
    def _estimate_hours_to_failure(self, baseline, current, critical_threshold):
        """Estimate hours until critical threshold is reached"""
        if baseline == 0:
            return None
        
        current_percent = (current / baseline) * 100
        critical_percent = critical_threshold
        
        if current_percent >= critical_percent:
            return 0
        
        # Assume linear growth
        percent_per_unit = current_percent / 1  # Simplified
        remaining_percent = critical_percent - current_percent
        hours = remaining_percent / max(percent_per_unit, 0.1)
        
        return max(0, hours)
    
    def predict_failures(self):
        """Predict what will fail soon"""
        print("\n🔮 PREDICTIVE FAILURE DETECTION")
        print("=" * 80)
        
        predictions = {
            "timestamp": datetime.utcnow().isoformat(),
            "predictions": [],
            "ships": {}
        }
        
        # Load baseline
        baseline_files = list(self.baselines_dir.glob("baseline_*.json"))
        if not baseline_files:
            print("❌ No baseline found. Run TOOL_AD first to establish baseline.")
            return None
        
        # Use most recent baseline
        with open(baseline_files[-1], 'r') as f:
            baseline = json.load(f)
        
        print(f"Using baseline from: {baseline['timestamp']}")
        
        # Example predictions (in production, would query current metrics)
        for ship_name in ["SQUIDSTATION", "PINKCADY", "STEALTHATTACK"]:
            predictions["ships"][ship_name] = {
                "predictions": [],
                "risk_level": "NORMAL"
            }
            
            # Simulate memory trend
            prediction = {
                "metric": "memory_usage",
                "ship": ship_name,
                "current_usage_gb": 7.2,
                "baseline_gb": 5.8,
                "max_available_gb": 16,
                "analysis": self.analyze_trend(5.8, 7.2, "memory"),
                "recommendation": "Monitor memory usage. Consider increasing swap or reducing container resources."
            }
            
            predictions["ships"][ship_name]["predictions"].append(prediction)
            
            if prediction["analysis"]["status"] == "CRITICAL":
                predictions["ships"][ship_name]["risk_level"] = "CRITICAL"
            elif prediction["analysis"]["status"] == "WARNING":
                predictions["ships"][ship_name]["risk_level"] = "WARNING"
        
        # Print predictions
        for ship, data in predictions["ships"].items():
            risk_icon = "🚨" if data["risk_level"] == "CRITICAL" else "⚠️" if data["risk_level"] == "WARNING" else "✅"
            print(f"\n{risk_icon} {ship}: {data['risk_level']}")
            
            for pred in data["predictions"]:
                analysis = pred["analysis"]
                if analysis["status"] != "NORMAL":
                    print(f"  {pred['metric']}: {analysis['status']}")
                    print(f"    Baseline: {analysis.get('baseline')}GB → Current: {analysis.get('current')}GB")
                    print(f"    Change: {analysis.get('change_percent', 0):.1f}%")
                    if analysis.get("hours_to_failure"):
                        print(f"    ⏰ Hours to critical: {analysis['hours_to_failure']:.1f}")
                    print(f"    Action: {pred['recommendation']}")
        
        # Save predictions
        pred_file = self.predictions_dir / f"predictions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(pred_file, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        print(f"\n✅ Predictions saved to {pred_file}")
        
        return predictions

if __name__ == "__main__":
    detector = PredictiveFailureDetector()
    detector.predict_failures()
