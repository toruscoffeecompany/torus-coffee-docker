# 🏴‍☠️ The Void Pirate Fleet — Augur Autonomous Trading Network

**Updated:** 2026-08-10T21:47:00Z  
**Fleet Commander:** Miss Pink (PINKCADY)  
**Fleet Admiral:** Sir Green (SQUIDSTATION)  
**Fleet Engineer:** Sir Azure (STEALTHATTACK)  

## 🌐 Network Topology

```
                    ┌──────────────────┐
                    │  Gatekeeper      │
                    │  192.168.0.1:1   │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌──────────┐       ┌──────────┐      ┌────────────┐
   │ PINKCADY │◄──────│ SQUIDSTA-│      │ STEALTHAT- │
   │ Miss Pink│ Tailscale │ TION   │◄────│ TACK       │
   │ 192.168.0.3│       │ Sir Green│      │ Sir Azure  │
   │ 100.106.235.103 │ │ 192.168.0.39│  │ 100.110.238.68│
   └──────────┘       │ 100.83.247.14│   └────────────┘
   │ TORUSLAPTOP      └──────────┘
   │ (Hidden Child)
   └────────────
```

## ⚡ Ship Manifest

| Ship | Role | IP | Tailscale | Key Services |
|------|------|----|-----------|--------------|
| **PINKCADY** | Torus Coffee Commander | 192.168.0.3 | 100.106.235.103 | POS:3100, Inventory:3200, Website:3000, Captain's Dashboard:8080, OODA daemon |
| **SQUIDSTATION** | Flagship (Sir Green) | 192.168.0.39 | 100.83.247.14 | TreasureMap:5000, Dashboard:8080, Grafana:3002, Prometheus:9090, Gitea:3000, cAdvisor:8081, Uptime Kuma:3001 |
| **STEALTHATTACK** | GPU Warfare | 192.168.0.32 | 100.110.238.68 | Docker:2375, ComfyUI:8188, Ollama:11434, RT-1B GPU |
| **TORUSLAPTOP** | Reconnaissance | ? | ? | Hidden child — fleet agent deployment pending |

## 🧠 Augur Auto-Learning Architecture

### How Augur Learns (F21.T3 — STEP_40)

```
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌─────────────┐
│ SIM LOOP    │───▶│ NSGA-II  │───▶│ VECTORBT │───▶│ HALL OF FAME│
│ 100+ epis.  │    │ 10-param │    │ Indep.   │    │ 11 gates    │
│ augur_sim_  │    │ evol.    │    │ Sharpe   │    │ + frozen    │
│ loop.py     │    │augur_    │    │ val.     │    │ JSON export │
│             │    │nsga2.py  │    │augur_    │    │ hall_of_     │
│             │    │          │    │vectorbt_ │    │ fame.py      │
└─────────────┘    └──────────┘    │ _check   │    └──────┬──────┘
                                   └──────────┘           │
                                                           ▼
┌──────────────┐    ┌───────────┐    ┌─────────────┐    ┌──────▼──────┐
│ SIGNAL GEN   │◀───│ AUTOpilot │◀───│ POSITION    │◀───│ PAPER TRADE │
│augur_signal_ │    │ augur_    │    │ augur_      │    │ augur_paper_│
│ generator.py │    │ autopilot │    │ position_   │    │ trader.py   │
│ eval genome  │    │ .py       │    │ monitor.py  │    │ Alpaca API  │
│ on tickers   │    │ 4-agent   │    │ fill track  │    │ bracket ord │
│ bot_signals  │    │ briefing  │    │ P&L → trades│    │ TP/SL legs  │
└──────────────┘    └───────────┘    └─────────────┘    └─────────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ LLM COACHING    │
                                  │ augur_coach.py  │
                                  │ qwen2.5:7b      │
                                  │ ai_coaching_log │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ AUTO-TUNE       │
                                  │ nightly retrain │
                                  │ with P&L feedbk │
                                  │ → back to NSGA-II
                                  └─────────────────┘
```

### Learning Cycle (Autonomous)

1. **Morning Briefing** (09:00 ET)
   - Regime Agent → classifies market (TRENDING_UP/RANGING/HIGH_VOL)
   - Scanner Agent → top 5 Augur picks matching regime
   - Risk Agent → open positions, circuit breaker status
   - Coach Agent → LLM synthesizes briefing (Ollama qwen2.5:7b on STEALTHATTACK)

2. **Signal Generation** (Continuous during market hours)
   - `augur_signal_generator.py` evaluates HOF genomes on live tickers
   - Results stored in `bot_signals` table
   - Scanner reads `bot_signals` scores + `price_history` indicators

3. **Paper Trading** (Market hours 09:30–15:45 ET)
   - `augur_paper_trader.py` converts picks to Alpaca PAPER orders
   - Hard-coded parameters: 2% risk, 2:1 R:R minimum, $100k paper account
   - Bracket orders with TP/SL legs

4. **Position Monitoring** (Every 30s)
   - `augur_position_monitor.py` tracks fills, P&L, R-multiples
   - Logs to `trades` + `order_log` tables

5. **Coaching** (Daily 23:00 CT)
   - `augur_coach.py` reviews yesterday's paper trades
   - LLM generates coaching notes → `ai_coaching_notes` table
   - Auto-tune: retrain if Sharpe dropped below threshold

### Auto-Tuning Parameters

| Genome | Params | Sharpe | WR | PF | Status |
|--------|--------|--------|----|----|--------|
| `sma_bounce` | SMA=20, R:R=2.0, ATR_stop_mult=0.5, rvol_min=0.3, max_hold=5d | 0.8 | 60% | 2.3 | ✅ ACTIVE |
| `vwap_bounce` | R:R=2.0, ATR_stop_mult=0.5, rvol_min=0.4, max_hold=3d | 0.4 | 60% | 2.3 | ⚠️ STANDBY |

## 🛡️ Safety & Risk Management

- **Paper Mode**: TRUE (hard-coded in augur_paper_trader.py — `_PAPER_MODE = 'paper'`)
- **Live Mode**: DISABLED (hard-coded `_LIVE_AUTHORIZED = False`)
- **Kill Trading**: False (OFF)
- **Kill Learning**: False (ON)
- **Captain Approval**: Required for live trades (Captain's `.env` has `CAPTAIN_APPROVAL_REQUIRED=True`)
- **Max Risk/Trade**: 2%
- **Max Positions**: 5
- **Min R:R**: 2.0
- **EOD Force Close**: 15:59 ET
- **Graduation Gate**: sim → Hall of Fame → Paper → Live (Captain-confirmed)

## 💰 Profit Reinvestment Plan

### Goal: Buy RTX 4090 for PINKCADY (Sir Azure's spare)
- **Target**: RTX 4090 (~$1,600) for STEALTHATTACK GPU upgrade
- **Funding**: Paper trading profits (no real money used)
- **Path**: Augur paper trades → demonstrate consistent 1% daily returns → Captain approval → real trading with $10 live account seed

### Current Paper Account
- **Account**: PA3LGB5OLZ2S (Alpaca Paper)
- **Cash**: $100,000
- **BP**: $99,684.40
- **Equity**: $100,001.00
- **Active positions**: AAPL (filled @ $306.61), BB (filled @ $8.99)
- **Paper P&L**: +$1.09 AAPL / -$0.09 BB (current)

## 🕸️ Fleet Orchestration

The `augur_autonomous_trainer.py` runs as a cron job every 5 minutes on PINKCADY, orchestrating all ships:

```python
# PINKCADY (local execution)
autonomous_loop(iterations=1, interval=300)
├── Phase 1: Data Infrastructure (check DB via TreasureMap API)
├── Phase 2: Network Knowledge Sync (read HOF from DB, write to Z:)
├── Phase 3: Signal Generation (POST /api/augur/batch_score)
├── Phase 4: Paper Trading (Alpaca PAPER API bracket orders)
├── Phase 5: Position Monitoring (Alpaca GET /positions, /orders)
└── Phase 6: Coaching (LLM notes, write to shared vault)
```

**Cron Schedule**: `every 5m` during market hours (09:00–16:15 ET)  
**Job ID**: `8911a015555d` (managed by Hermes scheduler)

## 📋 Trello Board Integration

| Board | ID | Owner | Purpose |
|-------|----|----|---------|
| Torus_Ops | 6a70a3157d0db4214ac3f9a3 | Miss Pink | Torus Coffee operations |
| VOID_Ops | 6a595669b8f8f99c93392f4f | Sir Green | Infrastructure / AI fleet |
| Connection Card | XikBHI8i | Both | Cross-board ticket routing |

## 🚀 Getting Started

```bash
# Run autonomously (cron job):
python augur_autonomous_trainer.py 1 5

# Run single cycle manually:
python augur_autonomous_trainer.py 1 0

# Run continuously (3 cycles, 5s apart):
python augur_autonomous_trainer.py 3 5

# Monitor paper positions:
python scripts/check_positions.py

# Check order details:
python scripts/check_order_details.py
```

---

⚓ **Crew Status**: PINKCADY ✅ ONLINE | SQUIDSTATION ✅ ONLINE | STEALTHATTACK ✅ ONLINE  
**Augur Status**: 🧠 Learning | 📈 Trading | 💰 Paper Profitable  
**Next Milestone**: Consistent 1% daily paper returns → Captain approval for $10 live seed