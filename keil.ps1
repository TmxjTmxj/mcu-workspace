# Run from any directory: & 'D:\codex\单片机\keil.ps1' doctor
$ErrorActionPreference = 'Stop'
$taskPython = if ($env:KEIL_PYTHON) { $env:KEIL_PYTHON } else { 'python' }
& $taskPython (Join-Path $PSScriptRoot 'keil_automation\scripts\keil_cli.py') @args
exit $LASTEXITCODE
