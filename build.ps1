# ==============================================================
# Pulsar AI Manager - Build Script
# ==============================================================
# Requirements: Python 3.13, Node.js 22
# Run from project root: .\build.ps1
# ==============================================================

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

# Bypass SOCKS proxy for all network tools
$env:no_proxy = "*"
$env:NO_PROXY  = "*"

function Step($n, $msg) {
    Write-Host ""
    Write-Host "[$n/4] $msg" -ForegroundColor Cyan
}

function Fail($msg) {
    Write-Host ""
    Write-Host "ERROR: $msg" -ForegroundColor Red
    Set-Location $Root
    exit 1
}

function Assert-Command($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Fail "'$cmd' not found in PATH. Please install it and retry."
    }
}

Write-Host ""
Write-Host " * PULSAR AI MANAGER - BUILD * " -ForegroundColor White -BackgroundColor DarkMagenta
Write-Host ""

Assert-Command "python"
Assert-Command "npm"

# ── Step 1: Backend (PyInstaller) ──────────────────────────
Step 1 "Building backend (PyInstaller)"

Set-Location "$Root\backend"

Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
python -m pip install pyinstaller --quiet --disable-pip-version-check
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

Write-Host "  Running PyInstaller..." -ForegroundColor Gray
python -m PyInstaller pulsar_backend.spec --clean --noconfirm

if (-not (Test-Path "dist\pulsar_backend\pulsar_backend.exe")) {
    Fail "pulsar_backend.exe was not created. Check PyInstaller output above."
}
Write-Host "  OK: backend\dist\pulsar_backend\" -ForegroundColor Green

# ── Step 2: Frontend (Vite) ────────────────────────────────
Step 2 "Building frontend (Vite + Electron mode)"

Set-Location "$Root\frontend"

$env:ELECTRON    = "1"
$env:VITE_API_URL = "http://127.0.0.1:8000"

Write-Host "  npm install..." -ForegroundColor Gray
npm install --silent

Write-Host "  npm run build..." -ForegroundColor Gray
npm run build

if (-not (Test-Path "dist\index.html")) {
    Fail "frontend\dist\index.html was not created. Check Vite output above."
}
Write-Host "  OK: frontend\dist\" -ForegroundColor Green

# ── Step 3: Copy frontend -> electron/renderer ─────────────
Step 3 "Copying frontend to electron\renderer"

$rendererDir = "$Root\electron\renderer"
if (Test-Path $rendererDir) { Remove-Item -Recurse -Force $rendererDir }
Copy-Item -Recurse "$Root\frontend\dist" $rendererDir

Write-Host "  OK: electron\renderer\" -ForegroundColor Green

# ── Step 4: Electron Builder (NSIS installer) ──────────────
Step 4 "Packaging installer (electron-builder)"

Set-Location "$Root\electron"

# Disable code signing (no certificate)
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
$env:CSC_LINK = ""
$env:WIN_CSC_LINK = ""

Write-Host "  npm install..." -ForegroundColor Gray
npm install --silent

Write-Host "  Building installer..." -ForegroundColor Gray
npm run build

$installer = Get-ChildItem "$Root\dist-electron" -Filter "*.exe" -ErrorAction SilentlyContinue |
             Select-Object -First 1

Set-Location $Root
Write-Host ""

if ($installer) {
    Write-Host "  BUILD COMPLETE!" -ForegroundColor Green
    Write-Host "  Installer: dist-electron\$($installer.Name)" -ForegroundColor Yellow
} else {
    Write-Host "  WARNING: no .exe found in dist-electron\" -ForegroundColor Yellow
}

Write-Host ""
