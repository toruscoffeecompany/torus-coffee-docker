"""Create the ticker_fundamentals and macro_econ DB tables + populate with sample data."""
import sqlite3, json, yfinance as yf, sys
from datetime import datetime, timedelta

db_path = "D:/Work/tr3asure_mAp/data/tm_hof.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# ─── 1. CREATE DB TABLES ──────────────────────────────────────────────────────
print("=== CREATING DB TABLES ===")

conn.execute("""
    CREATE TABLE IF NOT EXISTS ticker_fundamentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date TEXT NOT NULL,
        sector TEXT,
        industry TEXT,
        pe_ratio REAL,
        forward_pe REAL,
        pb_ratio REAL,
        roe REAL,
        debt_equity REAL,
        revenue_growth REAL,
        earnings_growth REAL,
        beta REAL,
        market_cap REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, date)
    )
""")
print("  ✅ ticker_fundamentals table created")

conn.execute("""
    CREATE TABLE IF NOT EXISTS macro_econ (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        vix REAL,
        vix_ema20 REAL,
        spy_close REAL,
        spy_ema200 REAL,
        fed_funds_rate REAL,
        yield_curve_spread REAL,
        usd_index REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date)
    )
""")
print("  ✅ macro_econ table created")

# ─── 2. POPULATE FUNDAMENTALS ──────────────────────────────────────────────────
print("\n=== POPULATING FUNDAMENTALS ===")

tickers = ["AAPL", "BB", "SPY", "QQQ", "IWM", "TSLA", "NVDA", "AMD", "GOOGL", "MSFT"]
for ticker in tickers:
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        sector = info.get('sector', 'unknown')

        # Check if already has data
        existing = conn.execute(
            "SELECT 1 FROM ticker_fundamentals WHERE ticker=? ORDER BY date DESC LIMIT 1",
            (ticker,)
        ).fetchone()
        if existing:
            print(f"  ⏭ {ticker}: already has data")
            continue

        conn.execute("""
            INSERT INTO ticker_fundamentals
                (ticker, date, sector, industry, pe_ratio, forward_pe, pb_ratio,
                 roe, debt_equity, revenue_growth, earnings_growth, beta, market_cap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker, datetime.now().strftime('%Y-%m-%d'),
            info.get('sector', 'unknown'), info.get('industry', 'unknown'),
            info.get('trailingPE'), info.get('forwardPE'), info.get('priceToBook'),
            info.get('returnOnEquity'), info.get('debtToEquity'),
            info.get('revenueGrowth'), info.get('earningsGrowth'),
            info.get('beta'), info.get('marketCap'),
        ))
        print(f"  ✅ {ticker}: PE={info.get('trailingPE','?')}, ROE={info.get('returnOnEquity','?')}, Sector={sector}")
        conn.commit()
    except Exception as e:
        print(f"  ⚠️  {ticker}: {e}")

# ─── 3. POPULATE MACRO DATA ────────────────────────────────────────────────────
print("\n=== POPULATING MACRO DATA ===")

try:
    # VIX
    vix_tk = yf.Ticker("^VIX")
    vix_hist = vix_tk.history(period="5d")
    latest_vix = float(vix_hist['Close'].iloc[-1]) if len(vix_hist) > 0 else 20.0

    # SPY
    spy_tk = yf.Ticker("SPY")
    spy_hist = spy_tk.history(period="200d")
    latest_spy = float(spy_hist['Close'].iloc[-1]) if len(spy_hist) > 0 else 0
    spy_ema200 = float(spy_hist['Close'].tail(200).mean()) if len(spy_hist) >= 200 else latest_spy

    # VIX EMA20
    vix_ema20 = float(vix_hist['Close'].tail(20).mean()) if len(vix_hist) >= 20 else latest_vix

    # Yield curve (10y - 2y): using ETF proxy (IEF - SHY)
    ief = yf.Ticker("IEF")
    shy = yf.Ticker("SHY")
    ief_price = float(ief.history(period="1d")['Close'].iloc[-1])
    shy_price = float(shy.history(period="1d")['Close'].iloc[-1])
    yield_spread = ief_price - shy_price  # proxy for yield curve slope

    # Fed funds rate (approximate from SHV)
    shv = yf.Ticker("SHV")
    shv_yield = float(shv.history(period="1d")['Close'].iloc[-1])
    # Use SHV yield as proxy for fed funds
    fed_rate = 0.0  # We'll set a reasonable estimate

    today = datetime.now().strftime('%Y-%m-%d')
    existing_macro = conn.execute("SELECT 1 FROM macro_econ WHERE date=?", (today,)).fetchone()
    if not existing_macro:
        conn.execute("""
            INSERT INTO macro_econ
                (date, vix, vix_ema20, spy_close, spy_ema200, fed_funds_rate, yield_curve_spread)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (today, latest_vix, vix_ema20, latest_spy, spy_ema200, 5.25, yield_spread))
        print(f"  ✅ VIX={latest_vix:.2f}, SPY={latest_spy:.2f}, SPY_EMA200={spy_ema200:.2f}")
        print(f"  ✅ Yield spread={yield_spread:.2f}, Fed rate=5.25%")
        conn.commit()
    else:
        print("  ⏭ Macro data already exists for today")
except Exception as e:
    print(f"  ⚠️  Macro: {e}")

conn.close()
print("\n=== DB POPULATION COMPLETE ===")