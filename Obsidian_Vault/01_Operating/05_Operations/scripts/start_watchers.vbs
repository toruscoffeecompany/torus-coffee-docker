Set WshShell = CreateObject("WScript.Shell")
' Check if pinkcady_comms_watcher.py is already running
Set objExec = WshShell.Exec("wmic process where """"name='pythonw.exe'"""" get CommandLine")
If InStr(objExec.StdOut.ReadAll, "pinkcady_comms_watcher.py") > 0 Then
    ' Watcher already running, skip
Else
    WshShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\Crew\pinkcady_comms_watcher.py" & chr(34), 0, False
End If
' Check if ooda_self_prompt_loop.py is already running
Set objExec2 = WshShell.Exec("wmic process where """"name='pythonw.exe'"""" get CommandLine")
If InStr(objExec2.StdOut.ReadAll, "ooda_self_prompt_loop.py") > 0 Then
    ' OODA already running, skip
Else
    WshShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\Crew\ooda_self_prompt_loop.py" & chr(34), 0, False
End If
Set WshShell = Nothing
