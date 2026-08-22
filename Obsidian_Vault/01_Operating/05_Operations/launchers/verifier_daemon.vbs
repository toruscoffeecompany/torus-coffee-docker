Set objShell = CreateObject("WScript.Shell")
' Use correct pythonw.exe path + suppress window (windowstyle=0 hidden)
objShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\Crew\verifier_daemon.py" & chr(34), 0, False
