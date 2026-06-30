param(
    [ValidateSet('Codex', 'ClaudeCode', 'Both')]
    [string]$Runtime = 'Codex',
    [string]$Destination,
    [string]$ClaudeDestination,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $repoRoot 'skills/agentic-code-review'

if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "Skill source not found: $source"
}

$resolvedSource = (Resolve-Path -LiteralPath $source).Path
$sourcePrefix = $resolvedSource.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

function Test-InstallExcludedPath {
    param([string]$RelativePath)

    $normalized = $RelativePath -replace '\\', '/'
    return (
        $normalized -match '(^|/)__pycache__/' -or
        $normalized -match '(^|/)\.pytest_cache/' -or
        $normalized -match '(^|/)\.mypy_cache/' -or
        $normalized -match '(^|/)\.ruff_cache/' -or
        $normalized -match '\.pyc$' -or
        $normalized -match '\.pyo$' -or
        $normalized -match '\.log$'
    )
}

function Get-CodexDestination {
    if ($Destination) {
        return $Destination
    }

    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    return (Join-Path $codexHome 'skills')
}

function Get-ClaudeDestination {
    if ($ClaudeDestination) {
        return $ClaudeDestination
    }

    $claudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
    return (Join-Path $claudeHome 'skills')
}

function Get-SelectedRuntimeNames {
    if ($Runtime -eq 'Both') {
        return @('Codex', 'ClaudeCode')
    }

    return @($Runtime)
}

function Assert-InstallTargetDoesNotOverlapSource {
    param([string]$FullTarget)

    $targetPrefix = $FullTarget.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

    if (
        $FullTarget.Equals($resolvedSource, [System.StringComparison]::OrdinalIgnoreCase) -or
        $targetPrefix.StartsWith($sourcePrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        $sourcePrefix.StartsWith($targetPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    ) {
        throw "Install target must not be the skill source or overlap it: $FullTarget"
    }
}

function New-InstallTarget {
    param(
        [string]$RuntimeName,
        [string]$DestinationPath,
        [object[]]$ExistingTargets
    )

    $unresolvedDestination = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($DestinationPath)
    $target = Join-Path $unresolvedDestination 'agentic-code-review'
    $fullTarget = [System.IO.Path]::GetFullPath($target)
    $targetPrefix = $fullTarget.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

    Assert-InstallTargetDoesNotOverlapSource -FullTarget $fullTarget

    foreach ($existing in $ExistingTargets) {
        $existingPrefix = $existing.FullTarget.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
        if (
            $fullTarget.Equals($existing.FullTarget, [System.StringComparison]::OrdinalIgnoreCase) -or
            $targetPrefix.StartsWith($existingPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
            $existingPrefix.StartsWith($targetPrefix, [System.StringComparison]::OrdinalIgnoreCase)
        ) {
            throw "Runtime install targets must not overlap: $fullTarget and $($existing.FullTarget)"
        }
    }

    New-Item -ItemType Directory -Force -Path $unresolvedDestination | Out-Null
    $resolvedDestination = (Resolve-Path -LiteralPath $unresolvedDestination).Path

    [pscustomobject]@{
        Runtime = $RuntimeName
        Destination = $resolvedDestination
        FullTarget = $fullTarget
    }
}

function Get-InstallSourceFiles {
    $gitFiles = @()
    try {
        $gitOutput = & git -C $repoRoot ls-files --cached --others --exclude-standard -- 'skills/agentic-code-review' 2>$null
        if ($LASTEXITCODE -eq 0) {
            $gitFiles = @($gitOutput | Where-Object { $_ })
        }
    }
    catch {
        $gitFiles = @()
    }

    if ($gitFiles.Count -gt 0) {
        foreach ($repoRelative in $gitFiles) {
            if (Test-InstallExcludedPath -RelativePath $repoRelative) {
                continue
            }

            $sourcePath = Join-Path $repoRoot $repoRelative
            if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
                continue
            }

            $relativeToSkill = $repoRelative -replace '^skills/agentic-code-review/', ''
            [pscustomobject]@{
                SourcePath = $sourcePath
                RelativePath = $relativeToSkill
            }
        }
        return
    }

    foreach ($file in Get-ChildItem -LiteralPath $source -Recurse -File -Force) {
        $relativeToSkill = $file.FullName.Substring($sourcePrefix.Length)
        if (Test-InstallExcludedPath -RelativePath $relativeToSkill) {
            continue
        }

        [pscustomobject]@{
            SourcePath = $file.FullName
            RelativePath = $relativeToSkill
        }
    }
}

if ($Runtime -eq 'ClaudeCode' -and $Destination) {
    throw '-Destination is Codex-specific. Use -ClaudeDestination with -Runtime ClaudeCode.'
}

if ($Runtime -eq 'Codex' -and $ClaudeDestination) {
    throw '-ClaudeDestination requires -Runtime ClaudeCode or -Runtime Both.'
}

$installTargets = @()
foreach ($runtimeName in Get-SelectedRuntimeNames) {
    $destinationPath = if ($runtimeName -eq 'Codex') { Get-CodexDestination } else { Get-ClaudeDestination }
    $installTargets += New-InstallTarget -RuntimeName $runtimeName -DestinationPath $destinationPath -ExistingTargets $installTargets
}

$installSourceFiles = @(Get-InstallSourceFiles)

foreach ($installTarget in $installTargets) {
    if (Test-Path -LiteralPath $installTarget.FullTarget) {
        if (-not $Force) {
            throw "Target already exists: $($installTarget.FullTarget). Re-run with -Force to replace it."
        }
        Remove-Item -LiteralPath $installTarget.FullTarget -Recurse -Force
    }

    New-Item -ItemType Directory -Force -Path $installTarget.FullTarget | Out-Null
    foreach ($entry in $installSourceFiles) {
        $destinationPath = Join-Path $installTarget.FullTarget $entry.RelativePath
        $destinationDirectory = Split-Path -Path $destinationPath -Parent
        New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
        Copy-Item -LiteralPath $entry.SourcePath -Destination $destinationPath -Force
    }
    Write-Host "Installed agentic-code-review for $($installTarget.Runtime) to $($installTarget.FullTarget)"
}
