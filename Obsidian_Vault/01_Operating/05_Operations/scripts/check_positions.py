import sys, json, urllib.request, base64

ALPACA_KEY = "PKGHX66PIW467YFQ2WFXSM7Y7I"
ALPACA_SECRET = "6rVGyGxu5PkkhNvozjKSXcNtfHV4qDgtpxjVymmSkDAa"

def alpaca_get(path):
    url = "https://paper-api.alpaca.markets/v2" + path
    creds = base64.b64encode(f"{ALPACA_KEY}:{ALPACA_SECRET}".encode()).decode()
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {creds}")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

print("=== OPEN POSITIONS ===")
positions = alpaca_get("/positions")
if isinstance(positions, list):
    print(f"Positions: {len(positions)}")
    for p in positions:
        print(f"  {p['symbol']}: {p['qty']} @ avg_entry={p['avg_entry_price']}")
        print(f"    Current: ${p.get('current_price','?')} | P/L: {p.get('unrealized_pl','?')} ({p.get('unrealized_plpc','?')}%)")
        tp = p.get('take_profit', {})
        sl = p.get('stop_loss', {})
        if tp:
            print(f"    TP: ${tp.get('limit_price','?')}")
        if sl:
            print(f"    SL: ${sl.get('stop_price','?')}")
else:
    print(f"Error: {str(positions)[:200]}")

print("\n=== OPEN ORDERS ===")
orders = alpaca_get("/orders?status=open")
if isinstance(orders, list):
    print(f"Open orders: {len(orders)}")
    for o in orders:
        print(f"  {o['symbol']}: {o['side']} {o['qty']} {o['type']} | class={o.get('order_class','?')} | status={o['status']}")
        tp = o.get('take_profit', {})
        sl = o.get('stop_loss', {})
        if tp:
            print(f"    TP: ${tp.get('limit_price','?')}")
        if sl:
            print(f"    SL: ${sl.get('stop_price','?')}")
        print(f"    ID: {o['id'][:8]}...")
else:
    print(f"Error: {str(orders)[:200]}")

print("\n=== CLOSED/PENDING ORDERS ===")
orders = alpaca_get("/orders?status=closed&limit=10")
if isinstance(orders, list):
    print(f"Recent orders: {len(orders)}")
    for o in orders:
        print(f"  {o['symbol']}: {o['side']} {o['qty']} | type={o['type']} | status={o['status']} | filled_avg={o.get('filled_avg_price','?')}")