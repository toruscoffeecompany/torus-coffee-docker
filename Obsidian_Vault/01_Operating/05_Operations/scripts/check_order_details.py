import json, urllib.request, base64

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

print("=== DETAILED ORDER ANALYSIS ===")
orders = alpaca_get("/orders?status=closed&limit=20")
if isinstance(orders, list):
    print(f"Total closed orders: {len(orders)}")
    for o in orders:
        oid = o.get('id', '?')[:8]
        sym = o.get('symbol', '?')
        side = o.get('side', '?')
        qty = o.get('qty', '?')
        typ = o.get('type', '?')
        status = o.get('status', '?')
        oclass = o.get('order_class', '?')
        filled = o.get('filled_avg_price', 'None')
        tp = o.get('take_profit', {})
        sl = o.get('stop_loss', {})
        legs = o.get('legs', [])

        print(f"  Order {oid}... | {sym} {side} {qty} {typ}")
        print(f"    class={oclass} | status={status} | filled_avg={filled}")
        if tp:
            print(f"    TP: limit={tp.get('limit_price','?')} | status={tp.get('status','?')}")
        if sl:
            print(f"    SL: stop={sl.get('stop_price','?')} | status={sl.get('status','?')}")
        if legs:
            print(f"    Legs ({len(legs)}):")
            for leg in legs:
                l_sym = leg.get('symbol', '?')
                l_side = leg.get('side', '?')
                l_status = leg.get('status', '?')
                l_price = leg.get('filled_avg_price', leg.get('limit_price', '?'))
                print(f"      {l_sym} {l_side} | status={l_status} | price={l_price}")

# Check the 2 open orders
print("\n=== OPEN ORDER DETAIL ===")
open_orders = alpaca_get("/orders?status=open")
if isinstance(open_orders, list):
    for o in open_orders:
        oid = o.get('id', '?')
        sym = o.get('symbol', '?')
        side = o.get('side', '?')
        qty = o.get('qty', '?')
        typ = o.get('type', '?')
        status = o.get('status', '?')
        oclass = o.get('order_class', '?')
        limit = o.get('limit_price', o.get('stop_price', '?'))
        legs = o.get('legs', [])
        print(f"  {sym} {side} {qty} {typ} | class={oclass} | status={status} | limit={limit}")
        if legs:
            for leg in legs:
                print(f"    Leg: {leg.get('symbol')} {leg.get('side')} status={leg.get('status')} price={leg.get('limit_price',leg.get('stop_price','?'))}")

# Account summary
print("\n=== ACCOUNT SUMMARY ===")
acct = alpaca_get("/account")
cash = acct.get('cash', '0')
bp = acct.get('buying_power', '0')
eq = acct.get('portfolio_value', '0')
print(f"Account: {acct.get('account_number','?')} | Status: {acct.get('status','?')}")
print(f"Cash: ${float(cash):,.2f} | BP: ${float(bp):,.2f} | Equity: ${float(eq):,.2f}")
print(f"Pattern Day Trader: {acct.get('pattern_day_trader','?')}")
print(f"Trading Blocked: {acct.get('trading_blocked','?')}")