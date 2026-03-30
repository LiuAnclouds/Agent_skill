param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }),
    [string[]]$SkillNames
)

$skillsRoot = Join-Path $RepoRoot "skills"
$targetRoot = Join-Path $CodexHome "skills"

if (!(Test-Path $skillsRoot)) {
    Write-Error "Skills directory not found: $skillsRoot"
    exit 1
}

New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null

if ($SkillNames -and $SkillNames.Count -gt 0) {
    $selected = @()
    foreach ($item in $SkillNames) {
        $selected += ($item -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }
} else {
    $selected = Get-ChildItem $skillsRoot -Directory | Sort-Object Name | Select-Object -ExpandProperty Name
}

foreach ($skill in $selected) {
    $src = Join-Path $skillsRoot $skill
    $dst = Join-Path $targetRoot $skill

    if (!(Test-Path $src)) {
        Write-Error "Skill not found in repository: $skill"
        exit 1
    }

    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    robocopy $src $dst /E /XD __pycache__ backups /XF *.pyc | Out-Null

    if ($LASTEXITCODE -ge 8) {
        Write-Error "robocopy failed for skill: $skill"
        exit $LASTEXITCODE
    }

    Write-Host "Installed: $skill -> $dst"
}

Write-Host ""
Write-Host "Done. Restart Codex or start a new session to load the updated skills."
