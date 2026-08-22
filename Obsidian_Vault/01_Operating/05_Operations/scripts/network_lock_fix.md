# Network Lock Fix — Tailscale + Docker Persistence on STEALTHATTACK

## Problem
When Windows profile is locked (not logged out), STEALTHATTACK loses:
- Tailscale connectivity (Wintun adapter drops)
- Docker network (daemon stops)
- Crew automation (Python daemons stop)

## Root Cause
Windows Fast User Switching kills network context for background sessions.

## Fix

### 1. Tailscale as Windows Service (Always-On)
```powershell
# Install Tailscale as a service (survives profile lock)
tailscale service install
sc config tailscale state= auto
sc config tailscaled state= auto
```

### 2. Registry: AlwaysOnline for Wintun
```reg
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\tailscale]
"Start"=dword:00000002
```

### 3. Persistent Route via NetSH
```cmd
netsh interface ipv4 add route 100.64.0.0/10 "tailscale0" store=persistent
```

### 4. Docker Daemon as Service
```powershell
# Configure Docker Desktop to run as background service
# In Docker Desktop Settings → General → "Start Docker Desktop when you log in" (keep OFF)
# Instead, use:
sc config com.docker.service start= auto
sc config com.docker.proxy start= auto
```

### 5. Crew Automation as Windows Service (NSSM)
```cmd
nssm install VOID_OODA "D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\pythonw.exe"
nssm set VOID_OODA AppDirectory "D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations"
nssm set VOID_OODA ApplicationArguments "Crew/ooa_permanent_daemon.py"
nssm start VOID_OODA
```

### 6. Auto-Reconnect on Unlock Event
Create Task Scheduler trigger on Event ID 4625 (bad login) or 4800 (workstation lock):
- Action: Run `tailscale up --reset` to force reconnect

## Deployment Checklist
- [x] Create fix scripts in `scripts/`
- [ ] Install NSSM on STEALTHATTACK
- [ ] Register OODA daemon as Windows service
- [ ] Configure Tailscale service mode
- [ ] Test profile lock → verify connectivity survives
- [ ] Document + notify crew
