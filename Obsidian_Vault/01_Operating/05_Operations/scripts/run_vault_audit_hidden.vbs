Set WshShell = CreateObject("WScript.Shell")
' Check if vault_audit.py is already running
Set objExec = WshShell.Exec("wmic process where ""name='pythonw.exe'"" get CommandLine")
If InStr(objExec.StdOut.ReadAll, "vault_audit.py") > 0 Then
    WScript.Quit
End If
WshShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\vault_audit.py" & chr(34), 0, False
Set WshShell = Nothing
