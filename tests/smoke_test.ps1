$ErrorActionPreference = "Stop"

$health = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health
Write-Output $health.Content
