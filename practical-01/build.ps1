param(
    [string]$Compiler = 'C:\msys64\ucrt64\bin\g++.exe'
)

$ErrorActionPreference = 'Stop'
$mpiRoot = Join-Path $PSScriptRoot '..\.tools\msmpi\ucrt64'
$buildDir = Join-Path $PSScriptRoot 'build'
if (-not (Test-Path -LiteralPath $Compiler)) { throw "Compiler not found: $Compiler" }
if (-not (Test-Path -LiteralPath "$mpiRoot\include\mpi.h")) {
    throw 'MPI headers not found. Run scripts\setup.ps1 first.'
}
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
foreach ($mode in @('unordered', 'ordered')) {
    & $Compiler -std=c++17 -O2 -Wall -Wextra -Wpedantic `
        "-I$mpiRoot\include" "-L$mpiRoot\lib" `
        "$PSScriptRoot\src\$mode.cpp" -o "$buildDir\$mode.exe" `
        -lmsmpi -static-libgcc -static-libstdc++
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $mode" }
}
Write-Host "Built: $buildDir"
