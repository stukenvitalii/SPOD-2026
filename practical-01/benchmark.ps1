param(
    [int[]]$Processes = @(1, 2, 4, 8, 16),
    [int[]]$Counts = @(1, 256, 16384),
    [ValidateRange(1, 2147483647)][int]$Rounds = 1000,
    [ValidateRange(1, 100)][int]$Repeats = 3
)

$ErrorActionPreference = 'Stop'
if (@($Processes | Where-Object { $_ -lt 1 -or $_ -gt 1024 }).Count) {
    throw 'Processes must be between 1 and 1024.'
}
if (@($Counts | Where-Object { $_ -lt 1 }).Count) { throw 'Counts must be positive.' }
$resultDir = Join-Path $PSScriptRoot 'results'
New-Item -ItemType Directory -Force -Path $resultDir | Out-Null
$output = Join-Path $resultDir ('timings-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '.csv')
'mode,processes,count,rounds,total_seconds,seconds_per_round,repeat' | Set-Content $output -Encoding utf8
foreach ($mode in @('unordered', 'ordered')) {
    foreach ($count in $Counts) {
        foreach ($processCount in $Processes) {
            & "$PSScriptRoot\run.ps1" -Mode $mode -Processes $processCount -Count $count -Rounds 10 -Benchmark | Out-Null
            for ($repeat = 1; $repeat -le $Repeats; ++$repeat) {
                $row = & "$PSScriptRoot\run.ps1" -Mode $mode -Processes $processCount -Count $count -Rounds $Rounds -Benchmark
                "$row,$repeat" | Add-Content $output -Encoding utf8
            }
        }
    }
}
Write-Host "Saved: $output"
