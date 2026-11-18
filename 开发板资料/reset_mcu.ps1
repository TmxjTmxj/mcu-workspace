$port = new-Object System.IO.Ports.SerialPort "COM20", 2400
$port.Open()
$port.RtsEnable = $true
Start-Sleep -Milliseconds 50
$port.RtsEnable = $false
Start-Sleep -Milliseconds 50
$port.Close()
