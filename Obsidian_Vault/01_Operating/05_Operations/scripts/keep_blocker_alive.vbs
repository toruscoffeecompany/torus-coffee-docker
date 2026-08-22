Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
lockFile = "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\cmd_popup_blocker.lock"
If Not fso.FileExists(lockFile) Then
    WshShell.Run chr(34) & "C:\Python314\pythonw.exe" & chr(34) & " " & chr(34) & "D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\cmd_popup_emergency_blocker.py" & chr(34), 0, False
End If
Set WshShell = Nothing
