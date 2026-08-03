# Sync the rrcat-tender skill between the workspace (this repo) and the
# installed skill directory, implementing ADR-001 directions:
#
#   SKILL.md                                          installed -> workspace
#   Examples/*.md, AGENTS.md, _template.docx          workspace -> installed
#
# Also normalizes all Examples/*.md to UTF-8 without BOM, mirrors Examples/
# to the installed dir (removing stale installed copies), and verifies
# integrity (SHA256 of SKILL.md + _template.docx, Examples counts,
# AGENTS.md presence).
#
# Usage (from the repo root):
#   powershell -ExecutionPolicy Bypass -File scripts/sync.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/sync.ps1 -Install   # bootstrap on first run
#   $env:RRCAT_SKILL_DIR = "C:\path\to\skill"; .\scripts\sync.ps1        # override install location
param([switch]$Install)

$ErrorActionPreference = "Stop"

$Workspace = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$InstallDir = if ($env:RRCAT_SKILL_DIR) { $env:RRCAT_SKILL_DIR } else { Join-Path $HOME ".agents\skills\rrcat-tender" }

function Say($msg) { Write-Host "sync: $msg" }
function Fail($msg) { Write-Error "ERROR: $msg"; exit 1 }

if (-not (Test-Path $Workspace\Examples)) { Fail "workspace not detected (no Examples\ at $Workspace)" }

if (-not (Test-Path $InstallDir)) {
    if ($Install) {
        Say "installed skill dir missing — bootstrapping $InstallDir from workspace"
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    } else {
        Fail "installed skill dir not found: $InstallDir
Run the sync once with -Install to bootstrap it from this workspace:
  powershell -ExecutionPolicy Bypass -File scripts\sync.ps1 -Install
Or set the RRCAT_SKILL_DIR environment variable to the installed skill location."
    }
}

# Bootstrap: seed the installed dir from the workspace when SKILL.md is absent
if ($Install -and -not (Test-Path (Join-Path $InstallDir "SKILL.md"))) {
    New-Item -ItemType Directory -Path (Join-Path $InstallDir "Examples") -Force | Out-Null
    Copy-Item "$Workspace\SKILL.md" $InstallDir -Force
    Copy-Item "$Workspace\AGENTS.md" $InstallDir -Force
    Copy-Item "$Workspace\_template.docx" $InstallDir -Force
    Get-ChildItem "$Workspace\Examples\*.md" | ForEach-Object { Copy-Item $_.FullName (Join-Path $InstallDir "Examples") -Force }
    Say "seeded installed dir from workspace (bootstrap)"
}

# 1. Normalize encoding: UTF-8 without BOM for all Examples\*.md
$utf8 = [System.Text.UTF8Encoding]::new($false)
Get-ChildItem "$Workspace\Examples\*.md" | ForEach-Object {
    $c = [System.IO.File]::ReadAllText($_.FullName)
    [System.IO.File]::WriteAllText($_.FullName, $c, $utf8)
}
Say "UTF-8 normalized (no BOM): Examples\*.md"

# 2. SKILL.md: installed -> workspace (canonical skill definition)
if (-not (Test-Path (Join-Path $InstallDir "SKILL.md"))) {
    Fail "installed SKILL.md missing at $InstallDir\SKILL.md — aborting (workspace copy kept)"
}
Copy-Item (Join-Path $InstallDir "SKILL.md") "$Workspace\SKILL.md" -Force
Say "SKILL.md: installed -> workspace"

# 3. Examples\*.md + AGENTS.md + _template.docx: workspace -> installed
New-Item -ItemType Directory -Path (Join-Path $InstallDir "Examples") -Force | Out-Null
$files = Get-ChildItem "$Workspace\Examples\*.md"
$files | ForEach-Object { Copy-Item $_.FullName (Join-Path $InstallDir "Examples") -Force }
# Mirror: remove installed examples that were deleted/renamed in the workspace
Get-ChildItem "$InstallDir\Examples\*.md" | ForEach-Object {
    if (-not (Test-Path (Join-Path $Workspace "Examples\$($_.Name)"))) {
        Remove-Item $_.FullName -Force
        Say "removed stale installed example: $($_.Name)"
    }
}
Copy-Item "$Workspace\AGENTS.md" $InstallDir -Force
Copy-Item "$Workspace\_template.docx" $InstallDir -Force
Say "Examples\*.md ($($files.Count) files), AGENTS.md, _template.docx: workspace -> installed (mirrored)"

# 4. Verify integrity
$failed = $false
foreach ($rel in @("SKILL.md", "_template.docx")) {
    $h1 = (Get-FileHash (Join-Path $InstallDir $rel) -Algorithm SHA256).Hash
    $h2 = (Get-FileHash (Join-Path $Workspace $rel) -Algorithm SHA256).Hash
    if ($h1 -eq $h2) { Say "SHA256 OK: $rel" } else { Say "SHA256 MISMATCH: $rel"; $failed = $true }
}
$wc = (Get-ChildItem "$Workspace\Examples\*.md").Count
$ic = (Get-ChildItem "$InstallDir\Examples\*.md").Count
Say "Examples count: workspace=$wc installed=$ic"
if ($wc -ne $ic) { Say "Examples count MISMATCH"; $failed = $true }
if (Test-Path (Join-Path $InstallDir "AGENTS.md")) {
    Say "AGENTS.md present in installed dir"
} else {
    Say "AGENTS.md MISSING in installed dir"; $failed = $true
}

if ($failed) { Fail "sync completed with integrity issues listed above" }
Say "Synced — all files verified."
