#!/usr/bin/env pwsh
# Sync vendored skills from their upstream repositories.
#
# Clones each upstream repo to a temporary directory, checks out the pinned
# commit, and copies the listed skill folders into skills/. Review the git
# diff afterwards, then commit.
#
# Usage:
#   .\scripts\sync-upstream.ps1
#
# Windows: PowerShell 5.1+ (or PowerShell 7+)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SkillsDir = Join-Path $RepoRoot "skills"
$TempRoot  = Join-Path ([System.IO.Path]::GetTempPath()) "smart-training-mcp-upstream"

# upstream repo URL -> (pinned commit, @{ source path = destination folder })
$Sources = @(
  @{
    Repo   = "https://github.com/disco-trooper/skills.git"
    Commit = "41bf668"
    Paths  = @{
      "cycling-training"     = "cycling-training"
      "hypertrophy-training" = "hypertrophy-training"
    }
  },
  @{
    Repo   = "https://github.com/borisghidaglia/science-based-lifter.git"
    Commit = "3718ff9"
    Paths  = @{
      "skills/schoenfeld-hypertrophy" = "schoenfeld-hypertrophy"
      "skills/sbs-training"            = "sbs-training"
      "skills/rp-training"             = "rp-training"
      "skills/rp-diet"                 = "rp-diet"
      "skills/program-creation"        = "program-creation"
      "skills/assessment"              = "assessment"
    }
  }
)

if (-not (Test-Path $SkillsDir)) {
  Write-Error "skills/ directory not found at $SkillsDir"
}

New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null

foreach ($src in $Sources) {
  $repoName = [System.IO.Path]::GetFileNameWithoutExtension($src.Repo)
  $cloneDir = Join-Path $TempRoot $repoName

  Write-Host ""
  Write-Host "== $($src.Repo) @ $($src.Commit)" -ForegroundColor Cyan

  if (Test-Path $cloneDir) {
    Remove-Item -LiteralPath $cloneDir -Recurse -Force
  }

  git clone --quiet $src.Repo $cloneDir
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to clone $($src.Repo)"
  }

  Push-Location $cloneDir
  try {
    git checkout --quiet $src.Commit
    if ($LASTEXITCODE -ne 0) {
      Write-Error "Failed to checkout commit $($src.Commit) in $($src.Repo)"
    }
  }
  finally {
    Pop-Location
  }

  foreach ($srcPath in $src.Paths.Keys) {
    $destName = $src.Paths[$srcPath]
    $srcDir   = Join-Path $cloneDir $srcPath
    $destDir  = Join-Path $SkillsDir $destName

    if (-not (Test-Path (Join-Path $srcDir "SKILL.md"))) {
      Write-Error "Expected SKILL.md not found in $srcDir"
    }

    Remove-Item -LiteralPath $destDir -Recurse -Force -ErrorAction SilentlyContinue
    robocopy $srcDir $destDir /E /NFL /NDL /NJH /NJS | Out-Null
    Write-Host "  [ok] $destName <- $srcPath" -ForegroundColor Green
  }
}

Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Sync complete. Review the changes with 'git diff' and commit." -ForegroundColor White
