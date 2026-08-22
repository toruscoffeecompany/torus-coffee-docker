$cpu = Get-CimInstance Win32_Processor
Write-Host "SVM: $($cpu.VirtualizationFirmwareEnabled)"
Write-Host "Virt: $($cpu.VirtualizationEnabled)"
Write-Host "SLAT: $($cpu.SecondLevelAddressTranslationExtensions)"
Write-Host "Cores: $($cpu.NumberOfCores)/$($cpu.NumberOfLogicalProcessors)"
