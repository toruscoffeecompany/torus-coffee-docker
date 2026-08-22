# PINKCADY Hidden Capabilities Audit
Date: 2026-08-06T00:30:00Z
Rig: PINKCADY (local Windows host)

## Verified hardware
- CPU: AMD Ryzen 5 3600 (6C/12T, 3.6GHz, 32MB L3)
- Motherboard: MSI MPG X570 GAMING PLUS (MS-7C37)
- RAM: 2x 8GB Corsair Vengeance CMW32GX4M4C3200C16 @ 2133 MHz (rated 3200)
- GPU: NVIDIA GeForce GT 1030 2GB
- Storage: T-FORCE 1TB (IDE reported) + Samsung SSD 970 EVO 500GB
- Network: Realtek GbE + Intel WiFi 6 AX200 + Bluetooth + Tailscale
- BIOS: AMI A.70 (2020-01-08)

## Current OS state
- Windows 10 Pro 22H2 build 19045
- Hyper-V services vmcompute/vmms: Running
- Virtualization firmware: Disabled
- Virtualization in OS: False
- Second Level Address Translation: Available

## Hidden/unlocked features
1. AMD-V / SVM Mode — disabled in BIOS, blocks Hyper-V/WSL2/containers
2. XMP/DOCP — RAM at 2133 instead of rated 3200
3. Precision Boost Overdrive / Curve Optimizer — available on Ryzen 3600, untapped
4. NVIDIA NVENC/NVDEC — GT 1030 can accelerate encode/decode
5. WSL2 / Hyper-V / Containers — Windows features likely uninstalled/disabled
6. Windows Sandbox / Credential Guard — available on Win10 Pro
7. CPU C-states / Cool'n'Quiet — power headroom
8. BIOS update available from MSI (2025 releases)

## What needs Captain/elevated action
- BIOS reboot to enable SVM Mode
- BIOS reboot to enable XMP/DOCP
- Optional: BIOS update
- Windows optional features install: Hyper-V, Virtual Machine Platform, WSL2, Containers

## Free-tier path
- Use Hyper-V or WSL2 for VMs
- Use Docker Desktop free tier
- Use Windows Sandbox for volatile testing
- No paid licenses required

## Risk notes
- BIOS update: requires stable power, USB flashdrive method if MSI Center fails
- XMP/DOCP: may need memory controller tuning on Ryzen 3000
- Virtualization enable: one-time reboot
