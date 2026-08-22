Set WshShell = CreateObject("WScript.Shell")
' Check if pythonw.exe is already running to avoid duplicates
Set objExec = WshShell.Exec("wmic process where name='pythonw.exe' get CommandLine")
If InStr(objExec.StdOut.ReadAll, "smart_ticket_cycle.py") > 0 Then
    WScript.Quit
End If
' Run pythonw.exe with FULL PATH — FIXED: use C:\Python314\pythonw.exe (NOT uv path)
WshShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\smart_ticket_cycle.py" & chr(34), 0, False
Set WshShell = Nothing
