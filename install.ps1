#!/usr/bin/env pwsh
# smart-training-mcp install script (Windows PowerShell)
#
# Creates symlinks for all skills into %USERPROFILE%\.agents\skills\
# Optionally sets up the Intervals.icu MCP server (Python + .env)
# and the paper-search MCP server (uvx + optional API keys).
#
# Usage:
#   .\install.ps1                 # Interactive setup
#   .\install.ps1 -Force          # Remove existing links before creating
#   .\install.ps1 -SkipMcp        # Skip MCP server setup
#   .\install.ps1 -SkipIntervals  # Set up paper search but skip Intervals.icu
#   .\install.ps1 -SkipPaperSearch  # Set up Intervals.icu but skip paper search

param(
    [switch]$Force,          # Remove existing links before creating
    [switch]$SkipMcp,        # Skip MCP server setup entirely
    [switch]$SkipIntervals,  # Skip Intervals.icu MCP setup
    [switch]$SkipPaperSearch # Skip paper-search MCP setup
)

$ErrorActionPreference = "Continue"

$RepoDir = $PSScriptRoot
$SkillsDir = "$env:USERPROFILE\.agents\skills"
$EnvExample = Join-Path $RepoDir "intervals-icu\.env.example"
$EnvFile = Join-Path $RepoDir "intervals-icu\.env"
$IcuDir = Join-Path $RepoDir "intervals-icu"
$PaperEnvExample = Join-Path $RepoDir "paper-search\.env.example"
$PaperEnvDir = "$env:USERPROFILE\.config\paper-search-mcp"
$PaperEnvFile = Join-Path $PaperEnvDir ".env"

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
    param($Source, $Name, $DestDir = $SkillsDir)

    $Dest = Join-Path $DestDir $Name

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
foreach ($name in @("running-training", "intervals-icu", "cycling-training", "hypertrophy-training", "schoenfeld-hypertrophy", "sbs-training", "rp-training", "rp-diet", "program-creation", "assessment", "paper-research")) {
    Link-Skill -Source "$RepoDir\skills\$name" -Name $name
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
$count = (Get-ChildItem $SkillsDir -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "$count skills in $SkillsDir" -ForegroundColor White

# ---------------------------------------------------------------------------
# Antigravity project-level customizations (.agents/)
#
# Antigravity does NOT read .mcp.json, .opencode/opencode.json, or the global
# ~/.agents/skills/. It discovers skills and MCP servers from .agents/ inside
# the workspace root, so this repo ships its own.
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Setting up Antigravity project-level customizations (.agents/)" -ForegroundColor Cyan

$AgentsSkillsDir = Join-Path $RepoDir ".agents\skills"
if (-not (Test-Path $AgentsSkillsDir)) {
    New-Item -ItemType Directory -Path $AgentsSkillsDir -Force | Out-Null
}

foreach ($name in @("running-training", "intervals-icu", "cycling-training", "hypertrophy-training", "schoenfeld-hypertrophy", "sbs-training", "rp-training", "rp-diet", "program-creation", "assessment", "paper-research")) {
    Link-Skill -Source "$RepoDir\skills\$name" -Name $name -DestDir $AgentsSkillsDir
}

# Antigravity plugins: MCP server definitions. These are checked in, so only
# write them when missing (or on -Force) to avoid clobbering local edits.
foreach ($plugin in @(
    @{ Name = "intervals-icu"; Content = @'
{
  "mcpServers": {
    "intervals-icu": {
      "command": "intervals-mcp",
      "args": []
    }
  }
}
'@ },
    @{ Name = "paper-search"; Content = @'
{
  "mcpServers": {
    "paper-search": {
      "command": "uvx",
      "args": ["--from", "paper-search-mcp", "--with", "mcp<2", "paper-search-mcp"]
    }
  }
}
'@ }
)) {
    $pdir = Join-Path $RepoDir ".agents\plugins\$($plugin.Name)"
    if (-not (Test-Path $pdir)) {
        New-Item -ItemType Directory -Path $pdir -Force | Out-Null
    }

    $manifest = @"
{
  "name": "$($plugin.Name)",
  "description": "MCP server integration for Smart Training"
}
"@
    $manifestPath = Join-Path $pdir "plugin.json"
    if (-not (Test-Path $manifestPath) -or $Force) {
        Set-Content -Path $manifestPath -Value $manifest -Force
    }

    $cfgPath = Join-Path $pdir "mcp_config.json"
    if (-not (Test-Path $cfgPath) -or $Force) {
        Set-Content -Path $cfgPath -Value $plugin.Content -Force
    }
    Write-Host "  [ok] .agents\plugins\$($plugin.Name)" -ForegroundColor Green
}

Write-Host "Antigravity setup: .agents\skills\ + .agents\plugins\ ready." -ForegroundColor Green

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

$IntervalsConfigured = $false

function Setup-IntervalsMcp {
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
    Write-Host "[!] No API key provided -- skipping Intervals.icu MCP setup." -ForegroundColor Yellow
    Write-Host "    Set it up later by running this script again" -ForegroundColor Yellow
    Write-Host "    or by manually editing intervals-icu/.env" -ForegroundColor Yellow
    return
}

$AthleteId = Read-Host "Enter your Intervals.icu athlete ID (e.g. i123456)"
if ([string]::IsNullOrWhiteSpace($AthleteId)) {
    Write-Host ""
    Write-Host "[!] No athlete ID provided -- skipping Intervals.icu MCP setup." -ForegroundColor Yellow
    Write-Host "    Set it up later by running this script again" -ForegroundColor Yellow
    Write-Host "    or by manually editing intervals-icu/.env" -ForegroundColor Yellow
    return
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

    # Step 5: Configure Antigravity CLI if installed
    $agyCmd = Get-Command agy -ErrorAction SilentlyContinue
    if ($null -ne $agyCmd) {
        try {
            & agy mcp add intervals-icu intervals-mcp 2>&1 | Out-Null
            Write-Host "[ok] Configured Intervals.icu in Antigravity CLI (agy)" -ForegroundColor Green
        } catch {
            Write-Verbose "Could not configure agy: $_"
        }
    }

    $script:IntervalsConfigured = $true
}
}

# ---------------------------------------------------------------------------
# paper-search MCP server setup (uvx + optional API keys)
# ---------------------------------------------------------------------------
function Setup-PaperSearchMcp {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host "Paper search MCP server setup" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host ""

    # Step 1: verify uv (required -- the server is launched via uvx)
    $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -eq $uvCmd) {
        Write-Host "[!] 'uv' not found -- the paper-search MCP server needs it." -ForegroundColor Yellow
        Write-Host "    Install from https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
        Write-Host "    Windows: winget install --id=astral-sh.uv -e" -ForegroundColor Yellow
        Write-Host "    Then re-run: .\install.ps1 -SkipIntervals" -ForegroundColor Yellow
        return
    }
    Write-Host "[ok] Found uv" -ForegroundColor Green

    # Step 2: optional API keys -> ~/.config/paper-search-mcp/.env (auto-loaded)
    if (Test-Path $PaperEnvFile) {
        Write-Host "[ok] $PaperEnvFile already exists (leaving it untouched)" -ForegroundColor Green
    } else {
        New-Item -ItemType Directory -Path $PaperEnvDir -Force | Out-Null
        Copy-Item $PaperEnvExample $PaperEnvFile -Force

        $UnpaywallEmail = Read-Host "Unpaywall email for OA lookups (any valid email; blank to skip)"
        if (-not [string]::IsNullOrWhiteSpace($UnpaywallEmail)) {
            $paperContent = Get-Content $PaperEnvFile -Raw
            $paperContent = $paperContent -replace 'PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=your_email_here', "PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=$UnpaywallEmail"
            Set-Content -Path $PaperEnvFile -Value $paperContent -NoNewline
            Write-Host "[ok] Written $PaperEnvFile" -ForegroundColor Green
            Write-Host "    Add optional keys (CORE, Semantic Scholar, OpenAlex) any time." -ForegroundColor Gray
        } else {
            Write-Host "[!] No email -- template written to $PaperEnvFile" -ForegroundColor Yellow
            Write-Host "    Paper search works keyless; Unpaywall stays disabled until set." -ForegroundColor Yellow
        }
    }

    # Step 3: warm the uvx cache so the first MCP call isn't slow
    Write-Host "Pre-downloading paper-search-mcp (first run only)..." -ForegroundColor Gray
    try {
        & uv run --quiet --with "paper-search-mcp" --with "mcp<2" python -c "import paper_search_mcp" 2>&1 | Out-Null
        Write-Host "[ok] paper-search-mcp ready" -ForegroundColor Green
    } catch {
        Write-Host "[!] Could not pre-download -- the first MCP call will do it instead." -ForegroundColor Yellow
    }

    # Step 4: register with Antigravity CLI if present
    $agyCmd = Get-Command agy -ErrorAction SilentlyContinue
    if ($null -ne $agyCmd) {
        try {
            & agy mcp add paper-search uvx -- --from paper-search-mcp --with "mcp<2" paper-search-mcp 2>&1 | Out-Null
            Write-Host "[ok] Configured paper-search in Antigravity CLI (agy)" -ForegroundColor Green
        } catch {
            Write-Verbose "Could not configure agy: $_"
        }
    }

    Write-Host ""
    Write-Host "Paper search is registered in .mcp.json and .opencode/opencode.json." -ForegroundColor Green
    Write-Host "Restart your client to load it. Then try:" -ForegroundColor Gray
    Write-Host '  "Find recent research on taper length before a marathon."' -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# Run setup
# ---------------------------------------------------------------------------
if (-not $SkipIntervals) {
    Setup-IntervalsMcp
} else {
    Write-Host ""
    Write-Host "Intervals.icu setup skipped (-SkipIntervals)." -ForegroundColor Gray
}

if (-not $SkipPaperSearch) {
    Setup-PaperSearchMcp
} else {
    Write-Host ""
    Write-Host "Paper search setup skipped (-SkipPaperSearch)." -ForegroundColor Gray
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  * Claude Code: skills and agents load automatically" -ForegroundColor Gray
Write-Host "  * OpenCode:    skills and agents load automatically" -ForegroundColor Gray
Write-Host "  * Antigravity: skills via .agents\skills\, MCP via .agents\plugins\" -ForegroundColor Gray
if ($IntervalsConfigured) {
    Write-Host "  * Intervals.icu: API key and athlete ID configured" -ForegroundColor Gray
}
if (-not $SkipPaperSearch) {
    Write-Host "  * Paper search: academic literature MCP server registered" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Restart your client (or run /mcp) to connect the servers." -ForegroundColor Gray
Write-Host ""
Write-Host "Self-contained: everything resolves inside this folder." -ForegroundColor DarkGray
Write-Host ""
