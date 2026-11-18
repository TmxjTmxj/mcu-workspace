$AiCube = "D:\keil\AiCube-ISP-v6.96V-plus.exe"
$HexFile = "D:\keil\开发板资料\STC8H工程标准框架\Outputs\Geek_STC8.hex"

if (-not (Test-Path $HexFile)) {
    Write-Host "ERROR: Hex file not found at $HexFile" -ForegroundColor Red
    exit 1
}

# Kill any existing AiCube process
Get-Process -Name "AiCube*" -ErrorAction SilentlyContinue | Stop-Process -Force

# Step 1: Reset MCU via RTS to trigger bootloader
Write-Host "[1/3] Resetting MCU to enter ISP bootloader..." -ForegroundColor Yellow
try {
    $port = New-Object System.IO.Ports.SerialPort "COM20", 115200
    $port.Open()
    $port.RtsEnable = $true
    Start-Sleep -Milliseconds 200
    $port.RtsEnable = $false
    $port.Close()
    Write-Host "  -> Reset OK (RTS toggled on COM20)" -ForegroundColor Green
} catch {
    Write-Host "  -> Could not auto-reset. Press RESET button manually." -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Step 2: Open AiCube-ISP
Write-Host "[2/3] Opening AiCube-ISP..." -ForegroundColor Yellow
$process = Start-Process -FilePath $AiCube -ArgumentList "`"$HexFile`"" -PassThru
Write-Host "  -> AiCube-ISP opened" -ForegroundColor Green
Start-Sleep -Seconds 3

# Step 3: Detect and program via GUI automation
Write-Host "[3/3] Ready for programming" -ForegroundColor Yellow
Write-Host ""
Write-Host "====== FLASH INSTRUCTIONS ======" -ForegroundColor Cyan
Write-Host "In the AiCube-ISP window:" -ForegroundColor White
Write-Host "  1. Check MCU type shows: STC8H8K64U" -ForegroundColor White
Write-Host "  2. Check hex file is loaded" -ForegroundColor White
Write-Host "  3. Click [Download/编程] button" -ForegroundColor Green
Write-Host "  4. Wait for 'ISP success!' message" -ForegroundColor White
Write-Host "=================================" -ForegroundColor Cyan
