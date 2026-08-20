$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$kanal = if ($args[0]) { $args[0] } else { "beispiel" }
New-Item -ItemType File -Force -Path (Join-Path $here "work\$kanal\.halt") | Out-Null
Write-Host "halt $kanal"
