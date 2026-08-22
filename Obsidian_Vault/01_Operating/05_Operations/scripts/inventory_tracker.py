"""
Torus Coffee Company - Freeze-Dried Inventory Tracker
Reads from/writes to Excel inventory file.
Schedule: Monthly via Windows Task Scheduler.
"""
import json
import os
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

VAULT = r"D:\Work\Torus Coffee Company LLC"
INVENTORY_FILE = os.path.join(VAULT, "04_Products", "Current Inventory.xlsx")
HISTORY_FILE = os.path.join(VAULT, "08_Reports", "_inventory_history.json")
MASTER_FILE = os.path.join(VAULT, "04_Products", "inventory_master.json")

SKUS = {
    "TCC-NOCC-200": "Neapolitan Orbit Cream Crunch",
    "TCC-OCC-200": "Orbit Cream Crunch",
    "TCC-SDB-115": "Star-Dusted Banana Crunch",
    "TCC-ACC-115": "Apple Cinnamon Comets",
    "TCC-ARB-26": "Aurora Berryalis",
    "TCC-SAB-26": "Sour Aurora Bites",
    "TCC-SS-05": "Solar Strawberries",
    "TCC-CB-155": "Cosmic Bananas",
    "TCC-AB-26": "Aurora Bites",
    "TCC-AZC-115": "Apple Zephyr Chips",
}

REORDER_POINTS = {
    "TCC-NOCC-200": 10,
    "TCC-OCC-200": 10,
    "TCC-SDB-115": 15,
    "TCC-ACC-115": 15,
    "TCC-ARB-26": 20,
    "TCC-SAB-26": 20,
    "TCC-SS-05": 15,
    "TCC-CB-155": 15,
    "TCC-AB-26": 20,
    "TCC-AZC-115": 15,
}


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_master():
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "r") as f:
            return json.load(f)
    return {"products": {sku: {"name": name, "qty": 0, "reorder_point": REORDER_POINTS.get(sku, 10)} for sku, name in SKUS.items()}}


def save_master(master):
    os.makedirs(os.path.dirname(MASTER_FILE), exist_ok=True)
    with open(MASTER_FILE, "w") as f:
        json.dump(master, f, indent=2)


def record_inventory(counts):
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "date": today,
        "counts": counts,
        "low_stock": [],
        "out_of_stock": [],
    }

    for sku, qty in counts.items():
        if qty == 0:
            entry["out_of_stock"].append(sku)
        elif qty < REORDER_POINTS.get(sku, 10):
            entry["low_stock"].append(sku)

    history[today] = entry
    save_history(history)
    return entry


def print_status(entry):
    print(f"Inventory snapshot: {entry['date']}")
    for sku, qty in entry["counts"].items():
        name = SKUS.get(sku, sku)
        flag = ""
        if sku in entry["out_of_stock"]:
            flag = " [OUT OF STOCK]"
        elif sku in entry["low_stock"]:
            flag = " [LOW STOCK]"
        print(f"  {name}: {qty}{flag}")


if __name__ == "__main__":
    if PANDAS_AVAILABLE and os.path.exists(INVENTORY_FILE):
        df = pd.read_excel(INVENTORY_FILE, sheet_name=None)
        latest_sheet = list(df.keys())[-1]
        latest_df = df[latest_sheet]
        
        counts = {}
        for _, row in latest_df.iterrows():
            sku = str(row.get("SKUs", "")).strip()
            if sku in SKUS:
                try:
                    qty = int(float(row.iloc[-1]))  # last column is most recent count
                    counts[sku] = qty
                except (ValueError, TypeError):
                    counts[sku] = 0
        
        entry = record_inventory(counts)
        print_status(entry)
        
        # Update master
        master = load_master()
        for sku, qty in counts.items():
            if sku in master["products"]:
                master["products"][sku]["qty"] = qty
                master["last_updated"] = entry["date"]
        save_master(master)
        print(f"\n✓ Master inventory updated")
    else:
        print("pandas not available or inventory file not found. Using sample data.")
        sample_counts = {sku: 0 for sku in SKUS}
        entry = record_inventory(sample_counts)
        print_status(entry)
