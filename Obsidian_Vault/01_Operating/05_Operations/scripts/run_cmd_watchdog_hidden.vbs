Set WshShell = CreateObject("WScript.Shell")
' FIX: Check if watchdog is already running via wmic before launching
' This prevents duplicate watchdog instances from the scheduled task
Set objExec = WshShell.Exec("wmic process where ""name='pythonw.exe'"" get CommandLine")
strOutput = objExec.StdOut.ReadAll
If InStr(strOutput, "cmd_popup_watchdog.py") > 0 Then
    ' Already running — exit without launching a duplicate
    WScript.Quit
End If
WshShell.Run """C:\Python314\pythonw.exe"" ""D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\cmd_popup_watchdog.py""", 0, False
Set WshShell = Nothing
