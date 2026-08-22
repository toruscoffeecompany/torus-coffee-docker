# Augur Profitability Gate — 20260810T182910Z

## Results: 2 trades

{
  "trade_count": 2,
  "open_trades": 2,
  "metrics": {
    "win_rate": 50.0,
    "total_pnl": 0.89,
    "avg_win": 1.04,
    "avg_loss": 0.15,
    "profit_factor": 6.9333,
    "sharpe": 0.0,
    "max_consecutive_losses": 1,
    "max_drawdown": 14.42
  },
  "gate_results": {
    "win_rate": {
      "value": 0.5,
      "threshold": 0.55,
      "passed": false
    },
    "profit_factor": {
      "value": 6.9333,
      "threshold": 1.2,
      "passed": true
    },
    "sharpe": {
      "value": 0.0,
      "threshold": 0.5,
      "passed": false
    },
    "consecutive_losses": {
      "value": 1,
      "threshold": 5,
      "passed": true
    },
    "drawdown": {
      "value": 0.1442,
      "threshold": 0.02,
      "passed": false
    },
    "total_profit": {
      "value": 0.89,
      "threshold": 1000.0,
      "passed": false
    }
  },
  "all_passed": false,
  "any_failed": true,
  "recommendation": "CONTINUE PAPER TRADING \u2014 retrain genome",
  "timestamp": "2026-08-10T23:29:10.692583+00:00"
}