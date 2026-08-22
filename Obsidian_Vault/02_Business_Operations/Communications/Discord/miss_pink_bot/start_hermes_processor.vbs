Set objShell = CreateObject("WScript.Shell")
strCmd = "C:\Users\torus\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe hermes_bridge_processor.py"
objShell.Run strCmd, 0, False