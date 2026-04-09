param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [ValidateSet("codex", "openclaw", "all")]
    [string]$Target = "codex",
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }),
    [string]$OpenClawHome = $(if ($env:OPENCLAW_HOME) { $env:OPENCLAW_HOME } else { Join-Path $env:USERPROFILE ".openclaw" }),
    [string[]]$SkillNames
)

$skillsRoot = Join-Path $RepoRoot "skills"

if (!(Test-Path $skillsRoot)) {
    Write-Error "Skills directory not found: $skillsRoot"
    exit 1
}

if ($SkillNames -and $SkillNames.Count -gt 0) {
    $selectionMode = "explicit"
    $selected = @()
    foreach ($item in $SkillNames) {
        $selected += ($item -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }
} else {
    $selectionMode = "auto"
    $selected = Get-ChildItem $skillsRoot -Directory -Force | Sort-Object Name | Select-Object -ExpandProperty Name
}

switch ($Target) {
    "all" { $targets = @("codex", "openclaw") }
    default { $targets = @($Target) }
}

$targetRoots = @{
    codex = Join-Path $CodexHome "skills"
    openclaw = Join-Path $OpenClawHome "skills"
}

foreach ($kind in $targets) {
    New-Item -ItemType Directory -Force -Path $targetRoots[$kind] | Out-Null
}

function Sync-Skill {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$SkillName,
        [string]$TargetName
    )

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    robocopy $Source $Destination /MIR /XD __pycache__ backups /XF *.pyc | Out-Null

    if ($LASTEXITCODE -ge 8) {
        Write-Error "robocopy failed for skill or bundle: $SkillName ($TargetName)"
        exit $LASTEXITCODE
    }

    Write-Host "Synced [$TargetName]: $SkillName -> $Destination"
}

foreach ($skill in $selected) {
    $src = Join-Path $skillsRoot $skill

    if (!(Test-Path $src)) {
        Write-Error "Skill or bundle not found in repository: $skill"
        exit 1
    }

    foreach ($kind in $targets) {
        if ($kind -eq "openclaw" -and $skill -eq ".system" -and $selectionMode -eq "auto") {
            Write-Host "Skipped [openclaw]: .system (hidden system bundle is skipped for OpenClaw by default)"
            continue
        }

        $dst = Join-Path $targetRoots[$kind] $skill
        Sync-Skill -Source $src -Destination $dst -SkillName $skill -TargetName $kind
    }
}

Write-Host ""
Write-Host "Done. Restart Codex/OpenClaw or start a new session to load the updated skills."
