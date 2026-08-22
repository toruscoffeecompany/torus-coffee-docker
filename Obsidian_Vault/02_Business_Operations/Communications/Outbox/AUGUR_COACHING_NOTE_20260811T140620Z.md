# 🧠 Augur Coaching Note — 20260811T140620Z

## Performance Review

### Current State
- **Paper Account**: PA3LGB5OLZ2S
- **Kill Trading**: False (OFF)
- **Kill Learning**: False (ON)
- **HOF Genomes**: Imported (sma_bounce Sharpe=0.8, vwap_bounce Sharpe=0.4)
- **Sims completed**: 4307
- **Active genome**: None — awaiting sim cycle

### Learning Pipeline Status
1. ✅ Data: yfinance CSVs imported into price_history (64,239 rows, 157 tickers)
2. ✅ HOF: 194 genomes imported via /api/augur/genomes/import
3. ✅ Signal Gen: batch_score producing entry zones for 157 tickers
4. ✅ Paper Trading: Alpaca paper orders active (BB + AAPL bracket orders)
5. ✅ Position Monitor: live via Alpaca API
6. ⏳ Coaching: LLM review pending (STEALTHATTACK qwen2.5:7b)

### Auto-Tune Recommendations
- sma_bounce (Sharpe=0.8): **KEEP ACTIVE** — above 0.5 threshold
- vwap_bounce (Sharpe=0.4): **RETIRED** for live scanning — below threshold
- Next retraining cycle: add 1-min bar data for intraday refinement
- BB not in price_history DB — add via Alpaca data feed

## Fleet Distribution
- **SQUIDSTATION**: sim loop, NSGA-II training, signal generation
- **PINKCADY**: paper trading, position monitoring, risk management
- **STEALTHATTACK**: LLM coaching, GPU-accelerated training
- **TORUSLAPTOP**: deploy hive-agent for fleet discovery
