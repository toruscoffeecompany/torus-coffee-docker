Set WshShell = CreateObject("WScript.Shell")
' Check if pythonw.exe is already running
Set objExec = WshShell.Exec("wmic process where ""name='pythonw.exe'"" get CommandLine")
If InStr(objExec.StdOut.ReadAll, "automated_verification.py") > 0 Then
    WScript.Quit
End If
WshShell.Run """C:\Python314\pythonw.exe"" ""D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\automated_verification.py""", 0, False
Set WshShell = Nothing
