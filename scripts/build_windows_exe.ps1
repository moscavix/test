param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist
}

python -m pip install --upgrade pip
python -m pip install -e . pyinstaller
pyinstaller --noconfirm --clean packaging/word-a11y-fixer.spec

Write-Host "Executable creato in: $RepoRoot\dist\WordAccessibilityFixer.exe"
