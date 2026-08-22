"""
START THE DISCORD CREW BOT — Miss Pink's instance (Scarlett Coralsink).
Uses pythonw.exe (no terminal window) per Captain's preferences.
Token: DISCORD_MISS_PINK_TOKEN (real, 72 chars) — verified in .env.
"""
import subprocess
import sys
import os

discord_dir = "Z:/Developer_Brain/02_Business_Operations/Communications/Discord"
runner_path = os.path.join(discord_dir, "run_miss_pink_bot.py")

# Find pythonw.exe
pythonw_candidates = [
    r"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\pythonw.exe",
    r"C:\Users\torus\AppData\Local\Programs\Python\Python311\pythonw.exe",
]
pythonw = None
for p in pythonw_candidates:
    if os.path.exists(p):
        pythonw = p
        break
if not pythonw:
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable  # fallback to regular python

# Check if bot is already running
result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
if "discord_crew_bot" in result.stdout:
    print("⚠️ Discord bot already running — not restarting")
else:
    # Start the bot runner directly with pythonw (no terminal window)
    print("=== Starting Miss Pink Discord bot (Scarlett Coralsink) ===")
    print(f"Launcher: {runner_path}")
    print(f"Executor: {pythonw}")
    print(f"Crew key: miss_pink (displays as Scarlett Coralsink)")

    try:
        proc = subprocess.Popen(
            [pythonw, runner_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"✅ Bot process started (PID: {proc.pid})")
        
        # Wait 3s and check
        import time
        time.sleep(3)
        proc_status = proc.poll()
        if proc_status is None:
            print(f"✅ Bot is RUNNING (still alive after 3s)")
        else:
            print(f"⚠️ Bot exited with code {proc_status} — checking for log output")
            # Try reading the log
            log_path = os.path.join(discord_dir, "bot_miss_pink.log")
            if os.path.exists(log_path):
                with open(log_path) as f:
                    content = f.read()
                print(f"Last log entries:")
                print(content[-500:] if len(content) > 500 else content)
            # Also try running with stderr captured
            proc2 = subprocess.run(
                [sys.executable, runner_path],
                capture_output=True, text=True, timeout=8
            )
            if proc2.stdout:
                print(f"stdout: {proc2.stdout[:500]}")
            if proc2.stderr:
                print(f"stderr: {proc2.stderr[:500]}")
    except Exception as e:
        print(f"❌ Failed to start: {e}")