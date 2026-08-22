Set WshShell = CreateObject("WScript.Shell")
' Check if master_ooda_loop.py is already running
Set objExec = WshShell.Exec("wmic process where ""name='pythonw.exe'"" get CommandLine")
If InStr(objExec.StdOut.ReadAll, "master_ooda_loop.py") > 0 Then
    WScript.Quit
End If
WshShell.Run """C:\Python314\pythonw.exe"" ""D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\master_ooda_loop.py""", 0, False
Set WshShell = Nothing
