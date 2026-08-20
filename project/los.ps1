param(
    [string]$Kanal = "beispiel",
    [int]$Bis = 10
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Root) { $Root = Get-Location }
Set-Location $PSScriptRoot
if ($Kanal -eq "beispiel") {
    $env:CHANNEL_SITE_BEISPIEL = "1"
    python .\run.py --beispiel --bis $Bis
} else {
    python .\run.py --kanal $Kanal --bis $Bis
}
