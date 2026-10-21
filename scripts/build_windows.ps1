param([string]$Python = "python", [switch]$Installer)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
function Invoke-Checked {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Exe failed with exit code $LASTEXITCODE" }
}
New-Item -ItemType Directory -Force .tmp, release | Out-Null
$env:TEMP = Join-Path (Get-Location) '.tmp'
$env:TMP = $env:TEMP
$env:PYINSTALLER_CONFIG_DIR = Join-Path (Get-Location) '.tmp\pyinstaller'
Invoke-Checked $Python @('-m', 'venv', '.venv-build')
$buildPython = Join-Path (Get-Location) '.venv-build\Scripts\python.exe'
Invoke-Checked $buildPython @('-m', 'pip', 'install', '--upgrade', 'pip')
Invoke-Checked $buildPython @('-m', 'pip', 'install', '.[build]')
Invoke-Checked $buildPython @('-m', 'unittest', 'discover', '-s', 'tests', '-v')
Invoke-Checked $buildPython @('scripts/smoke_gui.py')
Invoke-Checked $buildPython @('-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--onedir', '--name', 'PhoneNumberGenerator', '--paths', 'src', 'packaging\launcher.py')
$diagnosticFolder = Join-Path (Get-Location) ('.tmp\frozen-check-' + [guid]::NewGuid().ToString('N'))
$diagnosticProcess = Start-Process -FilePath (Join-Path (Get-Location) 'dist\PhoneNumberGenerator\PhoneNumberGenerator.exe') -ArgumentList '--self-test', ('"' + $diagnosticFolder + '"') -PassThru -Wait -WindowStyle Hidden
if ($diagnosticProcess.ExitCode -ne 0) { throw "Frozen GUI diagnostics failed. See $diagnosticFolder" }
Copy-Item -LiteralPath README.md, LICENSE -Destination dist\PhoneNumberGenerator
Compress-Archive -Path dist\PhoneNumberGenerator -DestinationPath release\PhoneNumberGenerator-Windows-Portable.zip -Force
Invoke-Checked $buildPython @('-m', 'build', '--no-isolation', '--outdir', 'release')
Invoke-Checked $buildPython @('scripts/package_source.py')
if ($Installer) {
    $compiler = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if (!$compiler) {
        $candidate = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
        if (!(Test-Path -LiteralPath $candidate)) {
            $candidate = Join-Path (Get-Location) '.tools\InnoSetup\ISCC.exe'
        }
        if (!(Test-Path -LiteralPath $candidate)) { throw 'Install Inno Setup 6 to build the installer.' }
        $compilerPath = $candidate
    } else { $compilerPath = $compiler.Source }
    Invoke-Checked $compilerPath @('packaging\windows.iss')
}
Get-ChildItem release -File | Where-Object Name -ne 'SHA256SUMS.txt' | Get-FileHash -Algorithm SHA256 | ForEach-Object {
    '{0}  {1}' -f $_.Hash.ToLower(), (Split-Path $_.Path -Leaf)
} | Set-Content release\SHA256SUMS.txt
Write-Host 'Packages are ready in release\.'
