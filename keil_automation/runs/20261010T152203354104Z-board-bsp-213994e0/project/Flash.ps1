$AiCube = "D:\keil\AiCube-ISP-v6.96V-plus.exe"
$HexFile = "D:\keil\开发板资料\STC8H工程标准框架\Outputs\Geek_STC8.hex"

if (-not (Test-Path $HexFile)) {
    Write-Host "ERROR: Hex file not found! Run Build.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "=== STC8H8K64U Flash Tool ===" -ForegroundColor Cyan
Write-Host "MCU: STC8H8K64U (via USB-HID)" -ForegroundColor White
Write-Host "Port: COM20 (CH340N)" -ForegroundColor White
Write-Host "Hex: $HexFile" -ForegroundColor White
Write-Host ""

# Reset MCU via RTS to enter bootloader mode
Write-Host "[1/2] Resetting MCU to bootloader mode..." -ForegroundColor Yellow
try {
    $port = New-Object System.IO.Ports.SerialPort "COM20", 115200
    $port.Open()
    $port.RtsEnable = $true
    Start-Sleep -Milliseconds 100
    $port.RtsEnable = $false
    $port.Close()
    Write-Host "  -> Reset signal sent via RTS (COM20)" -ForegroundColor Green
} catch {
    Write-Host "  -> WARNING: Could not reset via COM20: $_" -ForegroundColor Yellow
    Write-Host "  -> Please manually press the RESET button on the board" -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

# Open AiCube-ISP with hex file
Write-Host "[2/2] Opening AiCube-ISP..." -ForegroundColor Yellow
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  In AiCube-ISP:" -ForegroundColor White
Write-Host "  1. Verify MCU: STC8H8K64U (auto-detected)" -ForegroundColor White
Write-Host "  2. Verify Hex file is loaded" -ForegroundColor White
Write-Host "  3. Click [Download/编程] button" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Start-Process -FilePath $AiCube -ArgumentList "`"$HexFile`""
