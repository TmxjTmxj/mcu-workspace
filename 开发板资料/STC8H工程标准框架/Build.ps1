param(
    [switch]$Clean
)

$UV4 = "D:\keil\UV4\UV4.exe"
$Project = "D:\keil\开发板资料\STC8H工程标准框架\STC8.uvproj"
$Log = "D:\keil\开发板资料\STC8H工程标准框架\Outputs\build.log"

if ($Clean) {
    Write-Host "Cleaning project..." -ForegroundColor Yellow
    & $UV4 -c "$Project" -j0 -o "$Log"
} else {
    Write-Host "Building project..." -ForegroundColor Cyan
    & $UV4 -b "$Project" -j0 -o "$Log"
}

$logContent = Get-Content -Path $Log -Tail 5
Write-Host $logContent -ForegroundColor White

if ($logContent -match "0 Error\(s\)") {
    $hexFile = "D:\keil\开发板资料\STC8H工程标准框架\Outputs\Geek_STC8.hex"
    if (Test-Path $hexFile) {
        $size = (Get-Item $hexFile).Length
        Write-Host "`nBuild SUCCESS! Hex file: $hexFile ($size bytes)" -ForegroundColor Green
    }
    return $true
} else {
    Write-Host "`nBuild FAILED!" -ForegroundColor Red
    return $false
}
