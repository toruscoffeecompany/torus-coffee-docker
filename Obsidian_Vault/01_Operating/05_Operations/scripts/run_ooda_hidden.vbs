Set WshShell = CreateObject("WScript.Shell")
' Check if ooda_loop.py is already running
Set objExec = WshShell.Exec("wmic process where ""name='pythonw.exe'"" get CommandLine")
If InStr(objExec.StdOut.ReadAll, "ooda_loop.py") > 0 Then
    WScript.Quit
End If
WshShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\Crew\ooda_loop.py" & chr(34) & " --once", 0, False
Set WshShell = Nothing
