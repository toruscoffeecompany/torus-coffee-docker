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

# Get ALL orders (all statuses)
print("=== ALL ORDERS (most recent 25) ===")
all_orders = alpaca_get("/orders?status=all&limit=25&direction=desc")
if isinstance(all_orders, list):
    for o in all_orders:
        oid = o.get('id', '?')[:12]
        sym = o.get('symbol', '?')
        side = o.get('side', '?')
        qty = o.get('qty', '?')
        typ = o.get('type', '?')
        status = o.get('status', '?')
        cl_ord_id = o.get('client_order_id', '?')
        created = o.get('created_at', '?')[:19]
        filled = o.get('filled_avg_price', '-')
        oclass = o.get('order_class', '---')
        legs = o.get('legs', [])
        
        print(f"  {created} | {oid}... | {sym} {side} {qty} {typ}")
        print(f"    class={oclass} | status={status} | filled={filled} | client_id={cl_ord_id}")
        if legs:
            for leg in legs:
                l_status = leg.get('status', '?')
                l_price = leg.get('filled_avg_price', leg.get('limit_price', leg.get('stop_price', '-')))
                print(f"      Leg: {leg.get('symbol')} {leg.get('side')} | status={l_status} | price={l_price}")
        
        # Show TP/SL details
        tp = o.get('take_profit', {})
        sl = o.get('stop_loss', {})
        if tp:
            print(f"      TP: {tp.get('limit_price','?')} | status={tp.get('status','?')}")
        if sl:
            print(f"      SL: stop={sl.get('stop_price','?')} | status={sl.get('status','?')}")
