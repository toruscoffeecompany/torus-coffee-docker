
$proc = Get-WmiObject -Query "SELECT * FROM Win32_Process WHERE Name='cmd.exe'" 2>$null
if ($proc) {
    foreach ($p in $proc) {
        $parent = Get-WmiObject -Query "SELECT * FROM Win32_Process WHERE ProcessId=$($p.ParentProcessId)" 2>$null
        $parentCmd = if ($parent) { $parent.CommandLine } else { "unknown" }
        Write-Host "CMD_PID=$($p.ProcessId) PARENT=$parentCmd"
    }
} else {
    Write-Host "NO_CMD_RUNNING"
}
