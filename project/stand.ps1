$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$kanal = if ($args[0]) { $args[0] } else { "beispiel" }
$pfad = Join-Path $here "work\$kanal\stand.json"
if (Test-Path $pfad) { Get-Content $pfad -Raw } else { Write-Host "kein stand" }
