param(
    [string]$TrackerArgs,
    [string]$AnalysisArgs,
    [string]$MarineTrafficApiKey,
    [ValidateSet('query', 'path')]
    [string]$UrlStyle = 'path',
    [string]$Protocol = 'json',
    [string]$MsgType = 'extended',
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..\..\..')
$bashPath = 'C:\Program Files\Git\bin\bash.exe'
$trackerPath = 'skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh'
$analysisPath = 'skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-analysis.py'

function Show-Usage {
    @'
Usage:
  powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -TrackerArgs '--all'
  powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -TrackerArgs '--transit --period 24h'
  powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -AnalysisArgs '--summary'
  powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -TrackerArgs '--transit --period 24h' -MarineTrafficApiKey 'your_key'

Options:
  -TrackerArgs            Arguments passed to hormuz-tracker.sh
  -AnalysisArgs           Arguments passed to hormuz-analysis.py
  -MarineTrafficApiKey    Optional live API key
  -UrlStyle               query | path
  -Protocol               MarineTraffic protocol value, default json
  -MsgType                MarineTraffic msgtype value, default extended
  -Help                   Show this message
'@
}

if ($Help -or (-not $TrackerArgs -and -not $AnalysisArgs)) {
    Show-Usage
    exit 0
}

if (-not (Test-Path $bashPath)) {
    throw "Git Bash not found: $bashPath"
}

$bashCommands = @(
    "cd '/$($repoRoot.Path.Substring(0,1).ToLower())$($repoRoot.Path.Substring(2).Replace('\','/'))'"
)

if ($MarineTrafficApiKey) {
    $bashCommands += "export MARINETRAFFIC_API_KEY='$MarineTrafficApiKey'"
}

$bashCommands += "export MARINETRAFFIC_URL_STYLE='$UrlStyle'"
$bashCommands += "export MARINETRAFFIC_PROTOCOL='$Protocol'"
$bashCommands += "export MARINETRAFFIC_MSGTYPE='$MsgType'"

if ($TrackerArgs) {
    $bashCommands += "bash $trackerPath $TrackerArgs"
}

if ($AnalysisArgs) {
    $bashCommands += "python $analysisPath $AnalysisArgs"
}

$command = ($bashCommands -join '; ')

Write-Host "Running in Git Bash:" -ForegroundColor Cyan
Write-Host $command -ForegroundColor DarkGray

& $bashPath -lc $command
