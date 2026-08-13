#!/usr/bin/env pwsh
# smart-training-mcp install script (Windows PowerShell)
#
# Creates symlinks for all skills into %USERPROFILE%\.agents\skills\
# Optionally sets up the Intervals.icu MCP server (Python + .env).
#
# Usage:
#   .\install.ps1          # Interactive setup
#   .\install.ps1 -Force   # Remove existing links before creating
#   .\install.ps1 -SkipMcp # Skip MCP server setup

param(
    [switch]$Force,     # Remove existing links before creating
    [switch]$SkipMcp    # Skip MCP server setup entirely
)

$ErrorActionPreference = "Continue"

$RepoDir = $PSScriptRoot
$SkillsDir = "$env:USERPROFILE\.agents\skills"
$EnvExample = Join-Path $RepoDir "intervals-icu\.env.example"
$EnvFile = Join-Path $RepoDir "intervals-icu\.env"
$IcuDir = Join-Path $RepoDir "intervals-icu"

# ---------------------------------------------------------------------------
# Ensure skills directory exists
# ---------------------------------------------------------------------------
if (-not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

# ---------------------------------------------------------------------------
# Link a directory using symlink (preferred) or junction (fallback)
# ---------------------------------------------------------------------------
function Link-Skill {
    param($Source, $Name)

    $Dest = Join-Path $SkillsDir $Name

    if ($Force -or (Test-Path $Dest)) {
        if ((Get-Item $Dest -Force).LinkType -or (Test-Path $Dest)) {
            Remove-Item $Dest -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    if (Test-Path $Dest) {
        Write-Host "  [!] $Name already exists, skipping" -ForegroundColor Yellow
        return
    }

    # Try symbolic link first (requires Developer Mode or admin)
    try {
        New-Item -ItemType SymbolicLink -Path $Dest -Target $Source -Force -ErrorAction Stop | Out-Null
        Write-Host "  [ok] $Name" -ForegroundColor Green
        return
    } catch {
        Write-Verbose "Symlink failed, trying junction..."
    }

    # Fall back to directory junction (works without admin)
    try {
        New-Item -ItemType Junction -Path $Dest -Target $Source -Force -ErrorAction Stop | Out-Null
        Write-Host "  [ok] $Name (junction)" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] $Name failed: $_" -ForegroundColor Red
    }
}

# ---------------------------------------------------------------------------
# Install skills
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Installing skills to $SkillsDir" -ForegroundColor White
Write-Host "(works for Claude Code and OpenCode)" -ForegroundColor Gray
Write-Host ""

Write-Host "-- smart-training-mcp skills --" -ForegroundColor Cyan
foreach ($name in @("running-training", "intervals-icu", "cycling-training", "hypertrophy-training", "schoenfeld-hypertrophy", "sbs-training", "rp-training", "rp-diet", "program-creation", "assessment")) {
    Link-Skill -Source "$RepoDir\skills\$name" -Name $name
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
$count = (Get-ChildItem $SkillsDir -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "$count skills in $SkillsDir" -ForegroundColor White

# ---------------------------------------------------------------------------
# MCP server setup
# ---------------------------------------------------------------------------
if ($SkipMcp) {
    Write-Host ""
    Write-Host "MCP server setup skipped (-SkipMcp)." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  * Claude Code: skills and agents load automatically" -ForegroundColor Gray
    Write-Host "  * OpenCode:    skills and agents load automatically" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host "Intervals.icu MCP server setup" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "To connect to Intervals.icu, you need your API key and athlete ID."
Write-Host "Find them at: intervals.icu -> Settings -> Developer Settings"
Write-Host ""

# Step 1: Ask for credentials
$ApiKey = Read-Host "Enter your Intervals.icu API key"
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Host ""
    Write-Host "[!] No API key provided -- skipping MCP setup." -ForegroundColor Yellow
    Write-Host "    You can set it up later by running this script again" -ForegroundColor Yellow
    Write-Host "    or by manually editing intervals-icu/.env" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  * Claude Code: skills and agents load automatically" -ForegroundColor Gray
    Write-Host "  * OpenCode:    skills and agents load automatically" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

$AthleteId = Read-Host "Enter your Intervals.icu athlete ID (e.g. i123456)"
if ([string]::IsNullOrWhiteSpace($AthleteId)) {
    Write-Host ""
    Write-Host "[!] No athlete ID provided -- skipping MCP setup." -ForegroundColor Yellow
    Write-Host "    You can set it up later by running this script again" -ForegroundColor Yellow
    Write-Host "    or by manually editing intervals-icu/.env" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  * Claude Code: skills and agents load automatically" -ForegroundColor Gray
    Write-Host "  * OpenCode:    skills and agents load automatically" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Step 2: Write .env file
Copy-Item $EnvExample $EnvFile -Force
$envContent = Get-Content $EnvFile -Raw
$envContent = $envContent -replace 'API_KEY=your_intervals_api_key_here', "API_KEY=$ApiKey"
$envContent = $envContent -replace 'ATHLETE_ID=i123456', "ATHLETE_ID=$AthleteId"
Set-Content -Path $EnvFile -Value $envContent -NoNewline
Write-Host "[ok] Written intervals-icu/.env" -ForegroundColor Green

# Step 3: Set env vars persistently (user-level) and for current session
[Environment]::SetEnvironmentVariable("API_KEY", $ApiKey, "User")
[Environment]::SetEnvironmentVariable("ATHLETE_ID", $AthleteId, "User")
$env:API_KEY = $ApiKey
$env:ATHLETE_ID = $AthleteId
Write-Host "[ok] Set API_KEY and ATHLETE_ID (persistent + current session)" -ForegroundColor Green

# Step 4: Check Python and install MCP server
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            break
        }
    } catch {
        # Not found, try next
    }
}

if ($null -eq $pythonCmd) {
    Write-Host ""
    Write-Host "Python not found." -ForegroundColor Yellow

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($null -ne $winget) {
        Write-Host "winget is available -- installing Python 3.12..." -ForegroundColor Gray
        & winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null

        foreach ($cmd in @("python", "python3", "py")) {
            try {
                $version = & $cmd --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $pythonCmd = $cmd
                    break
                }
            } catch { }
        }

        if ($null -ne $pythonCmd) {
            Write-Host "[ok] Python installed via winget" -ForegroundColor Green
        } else {
            Write-Host "[!] winget install completed but Python not yet on PATH." -ForegroundColor Yellow
            Write-Host "    Close this terminal, open a NEW terminal, and run:" -ForegroundColor Yellow
            Write-Host "    cd intervals-icu; pip install ." -ForegroundColor Yellow
        }
    } else {
        Write-Host "[!] winget not available -- install Python manually:" -ForegroundColor Yellow
        Write-Host "    Download from https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "    Then run: cd intervals-icu; pip install ." -ForegroundColor Yellow
    }
}

if ($null -ne $pythonCmd) {
    Write-Host ""
    Write-Host "Found Python: $pythonCmd" -ForegroundColor Gray
    Write-Host "Installing intervals-icu MCP server..." -ForegroundColor Gray

    Push-Location $IcuDir
    try {
        & $pythonCmd -m pip install -e . --quiet 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[ok] Installed intervals-icu MCP server" -ForegroundColor Green
        } else {
            Write-Host "[!] pip install failed -- you can run it manually:" -ForegroundColor Yellow
            Write-Host "    cd intervals-icu; pip install ." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[!] pip install failed -- you can run it manually:" -ForegroundColor Yellow
        Write-Host "    cd intervals-icu; pip install ." -ForegroundColor Yellow
    }
    Pop-Location
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  * Claude Code: skills and agents load automatically" -ForegroundColor Gray
Write-Host "  * OpenCode:    skills and agents load automatically" -ForegroundColor Gray
Write-Host "  * Intervals.icu: API key and athlete ID configured" -ForegroundColor Gray
Write-Host ""
