$ErrorActionPreference = 'Stop'
foreach ($mode in @('unordered', 'ordered')) {
    foreach ($processCount in @(1, 2, 4, 8, 16)) {
        $rounds = 3
        $lines = @(& "$PSScriptRoot\run.ps1" -Mode $mode -Processes $processCount -Rounds $rounds)
        if ($lines.Count -ne $processCount * $rounds) { throw "Wrong line count: $mode/$processCount" }
        for ($round = 0; $round -lt $rounds; ++$round) {
            $ranks = @(
                for ($i = 0; $i -lt $processCount; ++$i) {
                    $line = $lines[$round * $processCount + $i]
                    if ($line -notmatch '^Hello from (\d+)$') { throw "Unexpected output: $line" }
                    [int]$Matches[1]
                }
            )
            if ($ranks[0] -ne 0) { throw 'Rank zero must be printed first.' }
            if ((($ranks | Sort-Object) -join ',') -ne ((0..($processCount - 1)) -join ',')) {
                throw "Missing or duplicate rank: $mode/$processCount"
            }
            if ($mode -eq 'ordered' -and ($ranks -join ',') -ne ((0..($processCount - 1)) -join ',')) {
                throw 'Ordered output is not sorted.'
            }
        }
        Write-Host "OK: $mode, $processCount processes, $rounds rounds"
    }
    $row = & "$PSScriptRoot\run.ps1" -Mode $mode -Processes 4 -Count 16384 -Rounds 20 -Benchmark
    $record = $row | ConvertFrom-Csv -Header mode, processes, count, rounds, total_seconds, seconds_per_round
    if ($record.mode -ne $mode -or $record.count -ne '16384' -or $record.rounds -ne '20') {
        throw 'Unexpected benchmark row.'
    }
    $elapsed = [double]::Parse($record.total_seconds, [Globalization.CultureInfo]::InvariantCulture)
    if ($elapsed -le 0) { throw 'Invalid benchmark timing.' }
    Write-Host "OK: $mode, 64 KiB messages, benchmark"
}
