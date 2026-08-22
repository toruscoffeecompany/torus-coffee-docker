"""
Start the Miss Pink bridge runner (miss_pink_bridge_runner.py).
Uses pythonw.exe (no terminal window) per Captain's preferences.
Also create a test message to verify the bridge works.
"""
import subprocess
import sys
import os
import time

# Paths
discord_dir = r"Z:/Developer_Brain/02_Business_Operations/Communications/Discord"
runner_path = os.path.join(discord_dir, "miss_pink_bridge_runner.py")
inbox_path = r"Z:/Developer_Brain/MISS_PINK_INBOX"
outbox_path = r"Z:/Developer_Brain/SIR_GREEN_INBOX"

# Find pythonw
pythonw = r"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\pythonw.exe"
if not os.path.exists(pythonw):
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")

# ─── 1. Create test message ─────────────────────────────────────────────────
os.makedirs(inbox_path, exist_ok=True)
test_msg_path = os.path.join(inbox_path, "TEST_20260811T030000Z_bridge_test.msg.md")
with open(test_msg_path, "w") as f:
    f.write("---\nfrom: test\nto: misspink\ntopic: bridge_test\nid: TEST_20260811T030000Z_bridge_test\nrequires_response: true\naction_required: false\nts: 2026-08-11T03:00:00Z\n---\n\nTest message for bridge runner verification. Please ACK.\n")
print("✅ Test message created in MISS_PINK_INBOX")

# ─── 2. Start the bridge runner ─────────────────────────────────────────────
print("\n=== Starting Miss Pink Bridge Runner ===")
print(f"Runner: {runner_path}")
print(f"Executor: {pythonw}")
print(f"INBOX: {inbox_path}")
print(f"OUTBOX: {outbox_path}")

# Check if already running
result = subprocess.run(["tasklist"], capture_output=True, text=True)
if "pythonw" in result.stdout and "2780" in result.stdout:
    # That's the Discord bot, not the bridge — different process
    pass

try:
    proc = subprocess.Popen(
        [pythonw, runner_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"✅ Bridge runner started (PID: {proc.pid})")
except Exception as e:
    print(f"❌ Failed: {e}")

# ─── 3. Wait + verify ────────────────────────────────────────────────────────
time.sleep(6)  # Wait > 5s polling interval + process startup

# Check for output
proc_status = proc.poll()
if proc_status is None:
    print(f"✅ Bridge runner is RUNNING (still alive after 6s)")
else:
    print(f"⚠️ Bridge runner exited with code {proc_status}")

# ─── 4. Verify the test message was processed ────────────────────────────────
print("\n=== Check if bridge processed the test message ===")
time.sleep(2)

outbox_files = os.listdir(outbox_path) if os.path.exists(outbox_path) else []
print(f"OUTBOX files: {len(outbox_files)}")

# Look for the ACK
test_ack = None
for f in outbox_files:
    if "TEST_20260811T030000Z" in f:
        test_ack = f
        break

if test_ack:
    ack_path = os.path.join(outbox_path, test_ack)
    with open(ack_path) as f:
        content = f.read()
    print(f"✅ ACK found: {test_ack}")
    print(f"   Content: {content[:200]}...")
else:
    print("⚠️ ACK not found yet — may need more time")
    # List all outbox files
    for f in outbox_files:
        print(f"   • {f}")

# Check the bridge log
log_path = r"Z:/Developer_Brain/logs/miss_pink_bridge.log"
if os.path.exists(log_path):
    with open(log_path) as f:
        log = f.read()
    print(f"\n✅ Bridge log exists ({len(log)} chars):")
    print(log[-300:] if len(log) > 300 else log)
else:
    print(f"\n⚠️ Bridge log not found — runner may not have started properly")

# ─── 5. Also clean up test message ───────────────────────────────────────────
try:
    os.remove(test_msg_path)
    if test_ack:
        os.remove(os.path.join(outbox_path, test_ack))
    print("\n✅ Test files cleaned up")
except:
    pass