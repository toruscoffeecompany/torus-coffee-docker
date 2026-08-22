# enable_windows_virtualization.ps1
# Run as Administrator after BIOS SVM Mode is enabled and PINKCADY has rebooted.
$ErrorActionPreference = 'Stop'
$log = "$PSScriptRoot\enable_windows_virtualization.log"

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $log -Value $line
}

Write-Log "=== Windows Virtualization Enablement ==="

# 1. Hyper-V
Write-Log "Enabling Hyper-V..."
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart | Out-Null
Write-Log "Hyper-V enable command completed."

# 2. Virtual Machine Platform
Write-Log "Enabling Virtual Machine Platform..."
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null
Write-Log "Virtual Machine Platform enable command completed."

# 3. WSL2
Write-Log "Enabling WSL2..."
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
Write-Log "WSL2 enable command completed."

# 4. Containers
Write-Log "Enabling Containers..."
dism.exe /online /enable-feature /featurename:Containers /all /norestart | Out-Null
Write-Log "Containers enable command completed."

# 5. Verify services
Write-Log "Verifying Hyper-V services..."
$services = @('vmcompute', 'vmms')
foreach ($svc in $services) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        Write-Log "$svc status: $($s.Status)"
        if ($s.Status -ne 'Running') {
            Write-Log "Starting $svc..."
            Start-Service -Name $svc -ErrorAction SilentlyContinue
        }
    } else {
        Write-Log "$svc not found."
    }
}

# 6. Verify virtualization status
Write-Log "Checking virtualization status..."
$cpu = Get-CimInstance Win32_Processor
Write-Log "VirtualizationEnabled: $($cpu.VirtualizationEnabled)"
Write-Log "VirtualizationFirmwareEnabled: $($cpu.VirtualizationFirmwareEnabled)"
Write-Log "SecondLevelAddressTranslationExtensions: $($cpu.SecondLevelAddressTranslationExtensions)"

Write-Log "=== Script complete. Please reboot if prompted. ==="
