# 🧠 Augur Learning Sync — 2026-08-13T00:16:19.336854+00:00

## Network Knowledge State — All Ships Synced

### 📊 Data Infrastructure
- **SQUIDSTATION**: 158 yfinance CSVs, 23 alpha_vantage, 2.3GB DB
- **PINKCADY**: Alpaca paper trading active, 2 bracket orders live
- **STEALTHATTACK**: GPT-2 model training, 31GB LLM models available

### 🧬 Hall of Fame Genomes (Imported: 5 active)
- `sma_bounce`: Sharpe=0.8, WR=60.0%, PF=2.3
- `sma_bounce`: Sharpe=0.8, WR=60.0%, PF=2.3
- `sma_bounce`: Sharpe=0.8, WR=60.0%, PF=2.3
- `sma_bounce`: Sharpe=0.8, WR=60.0%, PF=2.3
- `sma_bounce`: Sharpe=0.8, WR=60.0%, PF=2.3

### 📈 Market Regime: ``

### 🔄 How Augur Auto-Learns:
1. **NSGA-II** evolves 10-parameter genomes in `augur_nsga2.py` (on SQUIDSTATION)
2. **VectorBT** cross-validates Sharpe (independent check)
3. **HOF Promotion** — 11-criteria gate + VectorBT → frozen genome
4. **Signal Generation** — genome evaluated on live tickers → `bot_signals` table
5. **Autopilot** — regime → scanner → risk agent → picks with entry zones
6. **Paper Trading** — picks → Alpaca PAPER bracket orders (sma_bounce genome params)
7. **Position Monitor** — fills → P&L → R-multiples → `trades` + `order_log` tables
8. **Coaching** — LLM (Ollama qwen2.5:7b) reviews trades → `ai_coaching_notes`
9. **Auto-Tune** — nightly retrain using yesterday's P&L feedback
10. **Loop** — repeat, genomes get smarter every cycle

### 🎯 Auto-Tune Parameters (from Genome Catalog)
- `sma_bounce`: SMA=20, R:R=2.0, ATR_stop_mult=0.5, rvol_min=0.3, max_hold=5d
- `vwap_bounce`: R:R=2.0, ATR_stop_mult=0.5, rvol_min=0.4, max_hold=3d

### 🛡️ Safety Guards
- Paper mode: TRUE (hard-coded in augur_paper_trader.py)
- Max risk: 2% per trade, 5 max positions
- EOD force-close: 15:59 ET
- Kill switches: trading=OFF, learning=ON
