Set WshShell = CreateObject("WScript.Shell")

' Prevent duplicate OODAVRUR daemon instances
Set objExec = WshShell.Exec("wmic process where name='pythonw.exe' get CommandLine")
If InStr(objExec.StdOut.ReadAll, "oodavrur_engine.py") > 0 Then
    WScript.Quit
End If

' Run OODAVR engine in continuous mode (every 5 min)
WshShell.Run Chr(34) & "C:\Python314\pythonw.exe" & Chr(34) & " " & _
    Chr(34) & "D:\Work\.pirate_automation\scripts\oodavrur_engine.py" & Chr(34) & " --cycles 100 --delay 300", 0, False

Set WshShell = Nothing
