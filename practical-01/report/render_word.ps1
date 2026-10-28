$ErrorActionPreference = 'Stop'
$inputFile = Join-Path $PSScriptRoot 'Практическая работа 1 цветные графики.docx'
$qaDir = Join-Path $PSScriptRoot 'qa'
New-Item -ItemType Directory -Force -Path $qaDir | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $document = $word.Documents.Open($inputFile, $false, $true)
    $document.ExportAsFixedFormat((Join-Path $qaDir 'report.pdf'), 17)
    $document.Close(0)
} finally {
    $word.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
& pdftoppm -scale-to 1600 -png (Join-Path $qaDir 'report.pdf') (Join-Path $qaDir 'page')
if ($LASTEXITCODE -ne 0) { throw 'PDF rendering failed.' }
