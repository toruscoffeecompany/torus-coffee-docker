#!/usr/bin/env python3
import subprocess, sys, time, os
proc = subprocess.Popen([r"C:\Users\torus\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe", "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\02_Business_Operations\Communications\Discord\miss_pink_bot\hermes_bridge_processor.py"],
    cwd=r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\02_Business_Operations\Communications\Discord\miss_pink_bot", stdout=open(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\02_Business_Operations\Communications\Discord\miss_pink_bot\processor_monitor.log", 'a'), stderr=subprocess.STDOUT)
proc.wait()
