param([string]$Compiler = 'C:\msys64\ucrt64\bin\g++.exe')

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Compiler)) {
    throw 'Install MSYS2 and mingw-w64-ucrt-x86_64-gcc. See README.md.'
}
$mpiExec = Join-Path $env:ProgramFiles 'Microsoft MPI\Bin\mpiexec.exe'
if (-not (Test-Path -LiteralPath $mpiExec)) {
    & winget install --id Microsoft.msmpi --exact --source winget --accept-source-agreements --accept-package-agreements --silent --disable-interactivity
    if ($LASTEXITCODE -ne 0) { throw 'Microsoft MPI installation failed.' }
}
$toolDir = Join-Path $PSScriptRoot '..\.tools'
$downloadDir = Join-Path $toolDir 'downloads'
$sdkDir = Join-Path $toolDir 'msmpi'
New-Item -ItemType Directory -Force -Path $downloadDir, $sdkDir | Out-Null
$package = Join-Path $downloadDir 'msmpi.pkg.tar.zst'
$expectedHash = '34d22049cb785d7160c60b340409a70b0a006cb41967f75dfc331979d9788ab1'
if (-not (Test-Path -LiteralPath $package)) {
    Invoke-WebRequest -Uri 'https://mirror.msys2.org/mingw/ucrt64/mingw-w64-ucrt-x86_64-msmpi-10.1.1-26-any.pkg.tar.zst' -OutFile $package
}
if ((Get-FileHash $package -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'MPI package SHA-256 mismatch.'
}
& tar -xf $package -C $sdkDir
if ($LASTEXITCODE -ne 0) { throw 'Could not extract MPI package.' }
if (-not (Test-Path -LiteralPath $mpiExec)) { throw 'mpiexec.exe was not found after installation.' }
Write-Host 'MPI runtime and local GCC headers/library are ready.'
