$cpu = Get-CimInstance Win32_Processor
$mb = Get-CimInstance Win32_BaseBoard
$bios = Get-CimInstance Win32_BIOS
$mem = Get-CimInstance Win32_PhysicalMemory
$gpu = Get-CimInstance Win32_VideoController
$disk = Get-CimInstance Win32_DiskDrive
$nic = Get-CimInstance Win32_NetworkAdapter | Where-Object PhysicalAdapter -eq $true

Write-Host "=== CPU ==="
Write-Host "Name: $($cpu.Name)"
Write-Host "Cores/Threads: $($cpu.NumberOfCores)/$($cpu.NumberOfLogicalProcessors)"
Write-Host "MaxClockSpeed: $($cpu.MaxClockSpeed) MHz"
Write-Host "VirtualizationFirmwareEnabled: $($cpu.VirtualizationFirmwareEnabled)"
Write-Host "VirtualizationEnabled: $($cpu.VirtualizationEnabled)"
Write-Host "DataWidth: $($cpu.DataWidth)"
Write-Host "AddressWidth: $($cpu.AddressWidth)"
Write-Host "L2CacheSize: $($cpu.L2CacheSize)"
Write-Host "L3CacheSize: $($cpu.L3CacheSize)"

Write-Host ""
Write-Host "=== MOTHERBOARD ==="
Write-Host "Manufacturer: $($mb.Manufacturer)"
Write-Host "Product: $($mb.Product)"

Write-Host ""
Write-Host "=== BIOS ==="
Write-Host "Version: $($bios.SMBIOSBIOSVersion)"
Write-Host "ReleaseDate: $($bios.ReleaseDate)"

Write-Host ""
Write-Host "=== MEMORY ==="
$totalGB = [math]::Round(($mem | Measure-Object -Property Capacity -Sum | Select-Object -ExpandProperty Sum) / 1GB)
Write-Host "Total: $totalGB GB"
Write-Host "Slots: $($mem.Count)"

Write-Host ""
Write-Host "=== GPU ==="
foreach ($g in $gpu) {
    Write-Host "Name: $($g.Name)"
    Write-Host "RAM: $([math]::Round($g.AdapterRAM / 1MB)) MB"
    Write-Host "Driver: $($g.DriverVersion)"
}

Write-Host ""
Write-Host "=== DISKS ==="
foreach ($d in $disk) {
    Write-Host "Model: $($d.Model)"
    Write-Host "Size: $([math]::Round($d.Size / 1GB)) GB"
    Write-Host "Interface: $($d.InterfaceType)"
}

Write-Host ""
Write-Host "=== NETWORK ==="
foreach ($n in $nic) {
    Write-Host "Name: $($n.Name)"
    Write-Host "Speed: $([math]::Round($n.Speed / 1MB)) Mbps"
    Write-Host "MAC: $($n.MACAddress)"
}
