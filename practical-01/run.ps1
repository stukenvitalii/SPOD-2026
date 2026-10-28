param(
    [ValidateSet('unordered', 'ordered')][string]$Mode = 'unordered',
    [ValidateRange(1, 1024)][int]$Processes = 8,
    [ValidateRange(1, 2147483647)][int]$Rounds = 1,
    [ValidateRange(1, 2147483647)][int]$Count = 1,
    [switch]$Benchmark
)

$ErrorActionPreference = 'Stop'
$mpiExec = Join-Path $env:ProgramFiles 'Microsoft MPI\Bin\mpiexec.exe'
$program = Join-Path $PSScriptRoot "build\$Mode.exe"
if (-not (Test-Path -LiteralPath $mpiExec)) { throw 'Microsoft MPI is not installed.' }
if (-not (Test-Path -LiteralPath $program)) { throw 'Run build.ps1 first.' }
$env:PATH = "C:\msys64\ucrt64\bin;$env:PATH"
$programArgs = @('--rounds', "$Rounds", '--count', "$Count")
if ($Benchmark) { $programArgs += '--benchmark' }
& $mpiExec -n $Processes $program @programArgs
if ($LASTEXITCODE -ne 0) { throw "MPI program failed: $LASTEXITCODE" }
