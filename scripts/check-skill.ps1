param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

function Fail {
    param([string]$Message)
    throw "[agentic-code-review-skill] $Message"
}

function Assert-LineEndings {
    param(
        [string]$Path,
        [string]$RelativePath,
        [string]$ExpectedStyle
    )

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -eq 0) {
        return
    }

    if ($bytes[$bytes.Length - 1] -ne 10) {
        Fail "Missing final newline: $RelativePath"
    }

    for ($i = 0; $i -lt $bytes.Length; $i++) {
        if ($bytes[$i] -eq 13) {
            if ($i + 1 -ge $bytes.Length -or $bytes[$i + 1] -ne 10) {
                Fail "Invalid lone CR line ending in $RelativePath"
            }
            if ($ExpectedStyle -ne 'CRLF') {
                Fail "Expected LF line endings in $RelativePath"
            }
            $i++
        }
        elseif ($bytes[$i] -eq 10 -and $ExpectedStyle -ne 'LF') {
            Fail "Expected CRLF line endings in $RelativePath"
        }
    }
}

$repo = (Get-Item -LiteralPath $RepoRoot).FullName
$repoPrefix = $repo.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
$skill = Join-Path $repo 'skills/agentic-code-review'

$repositoryFiles = @()
try {
    $gitOutput = & git -C $repo ls-files --cached --others --exclude-standard 2>$null
    if ($LASTEXITCODE -eq 0) {
        $repositoryFiles = @($gitOutput | Where-Object { $_ })
    }
}
catch {
    $repositoryFiles = @()
}

if ($repositoryFiles.Count -eq 0) {
    $repositoryFiles = @(
        foreach ($file in Get-ChildItem -LiteralPath $repo -Recurse -File -Force) {
            $relative = $file.FullName.Substring($repoPrefix.Length) -replace '\\', '/'
            if ($relative -notlike '.git/*') {
                $relative
            }
        }
    )
}

$requiredFiles = @(
    '.editorconfig',
    '.gitattributes',
    '.gitignore',
    '.github/CODEOWNERS',
    '.github/dependabot.yml',
    '.github/ISSUE_TEMPLATE/config.yml',
    '.github/ISSUE_TEMPLATE/bug_report.md',
    '.github/ISSUE_TEMPLATE/feature_request.md',
    '.github/pull_request_template.md',
    '.github/workflows/validate.yml',
    'README.md',
    'CONTRIBUTING.md',
    'SECURITY.md',
    'SUPPORT.md',
    'CODE_OF_CONDUCT.md',
    'CHANGELOG.md',
    'LICENSE',
    'docs/bilingual-documentation.md',
    'docs/codebase-graph.md',
    'docs/agentic-code-review-source-notes.md',
    'docs/agentic-code-review-implementation-analysis.md',
    'docs/codex-claude-code-support-plan.md',
    'docs/source-refresh-checklist.md',
    'docs/open-source-readiness.md',
    'scripts/check-skill.ps1',
    'scripts/install-local.ps1',
    'tests/test_skill_scripts.py',
    'skills/agentic-code-review/SKILL.md',
    'skills/agentic-code-review/agents/openai.yaml',
    'skills/agentic-code-review/scripts/collect_github_metrics.py',
    'skills/agentic-code-review/scripts/detect_review_fix_loop.py',
    'skills/agentic-code-review/scripts/measure_diff.py',
    'skills/agentic-code-review/scripts/validate_batch_triage.py',
    'skills/agentic-code-review/scripts/validate_hostile_fixtures.py',
    'skills/agentic-code-review/scripts/validate_metrics.py',
    'skills/agentic-code-review/scripts/validate_reviewer_comparison.py',
    'skills/agentic-code-review/references/review-intake.md',
    'skills/agentic-code-review/references/review-effort-signals.md',
    'skills/agentic-code-review/references/risk-model.md',
    'skills/agentic-code-review/references/review-depth.md',
    'skills/agentic-code-review/references/test-change-review.md',
    'skills/agentic-code-review/references/heterogeneous-reviewers.md',
    'skills/agentic-code-review/references/reviewer-prompts.md',
    'skills/agentic-code-review/references/llm-security-review.md',
    'skills/agentic-code-review/references/ci-gate-integrity.md',
    'skills/agentic-code-review/references/batch-triage.md',
    'skills/agentic-code-review/references/human-on-the-loop-audit.md',
    'skills/agentic-code-review/references/team-adoption-metrics.md',
    'skills/agentic-code-review/references/output-format.md',
    'skills/agentic-code-review/references/examples.md',
    'skills/agentic-code-review/references/adoption.md',
    'skills/agentic-code-review/references/integrations/review-fix-loop.md',
    'skills/agentic-code-review/assets/AGENTS.snippet.md',
    'skills/agentic-code-review/assets/CLAUDE.snippet.md',
    'skills/agentic-code-review/assets/pull_request_template.md',
    'skills/agentic-code-review/assets/batch-triage.template.json',
    'skills/agentic-code-review/assets/batch-triage.schema.json',
    'skills/agentic-code-review/assets/forward-test-scenarios.json',
    'skills/agentic-code-review/assets/hostile-input-fixtures.md',
    'skills/agentic-code-review/assets/hostile-input-fixtures.json',
    'skills/agentic-code-review/assets/review-effort.config.example.json',
    'skills/agentic-code-review/assets/review-fix-loop.gates.example.json',
    'skills/agentic-code-review/assets/review-capacity-metrics.template.csv',
    'skills/agentic-code-review/assets/review-capacity-metrics.schema.json',
    'skills/agentic-code-review/assets/reviewer-comparison.example.json',
    'skills/agentic-code-review/assets/reviewer-comparison.template.md',
    'skills/agentic-code-review/assets/reviewer-comparison.schema.json'
)

$localizedMarkdown = @(
    'README.md',
    'CONTRIBUTING.md',
    'SECURITY.md',
    'SUPPORT.md',
    'CODE_OF_CONDUCT.md',
    'CHANGELOG.md',
    'docs/bilingual-documentation.md',
    'docs/codebase-graph.md',
    'docs/agentic-code-review-source-notes.md',
    'docs/agentic-code-review-implementation-analysis.md',
    'docs/codex-claude-code-support-plan.md',
    'docs/source-refresh-checklist.md',
    'docs/open-source-readiness.md',
    '.github/pull_request_template.md',
    '.github/ISSUE_TEMPLATE/bug_report.md',
    '.github/ISSUE_TEMPLATE/feature_request.md',
    'skills/agentic-code-review/SKILL.md',
    'skills/agentic-code-review/references/review-intake.md',
    'skills/agentic-code-review/references/review-effort-signals.md',
    'skills/agentic-code-review/references/risk-model.md',
    'skills/agentic-code-review/references/review-depth.md',
    'skills/agentic-code-review/references/test-change-review.md',
    'skills/agentic-code-review/references/heterogeneous-reviewers.md',
    'skills/agentic-code-review/references/reviewer-prompts.md',
    'skills/agentic-code-review/references/llm-security-review.md',
    'skills/agentic-code-review/references/ci-gate-integrity.md',
    'skills/agentic-code-review/references/batch-triage.md',
    'skills/agentic-code-review/references/human-on-the-loop-audit.md',
    'skills/agentic-code-review/references/team-adoption-metrics.md',
    'skills/agentic-code-review/references/output-format.md',
    'skills/agentic-code-review/references/examples.md',
    'skills/agentic-code-review/references/adoption.md',
    'skills/agentic-code-review/references/integrations/review-fix-loop.md',
    'skills/agentic-code-review/assets/AGENTS.snippet.md',
    'skills/agentic-code-review/assets/CLAUDE.snippet.md',
    'skills/agentic-code-review/assets/hostile-input-fixtures.md',
    'skills/agentic-code-review/assets/pull_request_template.md'
)

foreach ($relative in $requiredFiles) {
    $path = Join-Path $repo $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Fail "Missing required file: $relative"
    }
}

function Get-ZhCnPath {
    param([string]$RelativePath)

    $directory = Split-Path -Path $RelativePath -Parent
    $fileName = Split-Path -Path $RelativePath -Leaf
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
    $extension = [System.IO.Path]::GetExtension($fileName)
    $localizedName = "$stem.zh-CN$extension"
    if ($directory) {
        return (Join-Path $directory $localizedName)
    }
    return $localizedName
}

function Get-MarkdownHeadingCount {
    param([string]$Text)

    $matches = [regex]::Matches($Text, '(?m)^#{1,6}\s+')
    return $matches.Count
}

function Assert-LocalizedMarkerParity {
    param(
        [string]$RelativePath,
        [string]$ZhRelativePath,
        [string]$EnglishText,
        [string]$ZhText
    )

    $markerChecks = @(
        [pscustomobject]@{ Name = 'Not reviewable'; English = 'Not reviewable'; Chinese = 'Not reviewable|\u4E0D\u53EF\u8BC4\u5BA1' },
        [pscustomobject]@{ Name = 'Needs confirmation'; English = 'Needs confirmation'; Chinese = 'Needs confirmation|\u5F85\u786E\u8BA4|\u9700\u8981\u786E\u8BA4' },
        [pscustomobject]@{ Name = 'risk tier'; English = '(?i)\bL[0-4]\b|risk tier'; Chinese = '(?i)\bL[0-4]\b|\u98CE\u9669' },
        [pscustomobject]@{ Name = 'validation'; English = '(?i)validation|checks run|test output'; Chinese = '(?i)validation|\u9A8C\u8BC1|\u6821\u9A8C|\u68C0\u67E5' },
        [pscustomobject]@{ Name = 'human owner'; English = '(?i)human owner|human merge owner|human ownership'; Chinese = '(?i)human|\u4EBA\u7C7B|\u8D1F\u8D23\u4EBA|owner' },
        [pscustomobject]@{ Name = 'decision log'; English = '(?i)decision log'; Chinese = '(?i)decision log|\u51B3\u7B56\u65E5\u5FD7' },
        [pscustomobject]@{ Name = 'slice map'; English = '(?i)slice map'; Chinese = '(?i)slice map|\u5207\u7247\u56FE' },
        [pscustomobject]@{ Name = 'CI gate'; English = '(?i)\bCI\b|gate integrity|required checks|coverage|lint|security scans|dependency policy|release metadata'; Chinese = '(?i)\bCI\b|gate|checks|lint|coverage|\u5B8C\u6574\u6027|\u8986\u76D6\u7387|\u5B89\u5168|\u4F9D\u8D56|\u53D1\u5E03' },
        [pscustomobject]@{ Name = 'LLM trust boundary'; English = '(?i)LLM|prompt|trust boundary|tool-action'; Chinese = '(?i)LLM|prompt|\u4FE1\u4EFB\u8FB9\u754C|tool|\u5DE5\u5177' },
        [pscustomobject]@{ Name = 'heterogeneous reviewers'; English = '(?i)heterogeneous|independent review|reviewer calibration'; Chinese = '(?i)heterogeneous|\u5F02\u6784|\u72EC\u7ACB|reviewer|\u6821\u51C6' }
    )

    foreach ($check in $markerChecks) {
        if ($EnglishText -match $check.English -and $ZhText -notmatch $check.Chinese) {
            Fail "Localized Markdown marker drift for '$($check.Name)': $RelativePath vs $ZhRelativePath"
        }
    }
}

function Assert-SkillFrontmatter {
    param([string]$Text)

    $match = [regex]::Match($Text, '(?s)\A---\r?\n(?<Body>.*?)\r?\n---\r?\n')
    if (-not $match.Success) {
        Fail 'SKILL.md must start with YAML frontmatter.'
    }

    $lines = $match.Groups['Body'].Value -split '\r?\n'
    $keys = @()
    foreach ($line in $lines) {
        if ($line -notmatch '^(name|description):\s*.+$') {
            Fail "SKILL.md frontmatter contains unsupported or empty field: $line"
        }
        $keys += ($line -replace ':.*$', '')
    }

    $expectedKeys = @('name', 'description')
    if ($keys.Count -ne $expectedKeys.Count) {
        Fail 'SKILL.md frontmatter must contain exactly name and description.'
    }
    for ($i = 0; $i -lt $expectedKeys.Count; $i++) {
        if ($keys[$i] -ne $expectedKeys[$i]) {
            Fail 'SKILL.md frontmatter fields must be ordered as name then description.'
        }
    }
    if (($lines[0] -replace '^name:\s*', '') -ne 'agentic-code-review') {
        Fail 'SKILL.md frontmatter name must be agentic-code-review.'
    }
}

$skillText = Get-Content -LiteralPath (Join-Path $skill 'SKILL.md') -Raw -Encoding UTF8
Assert-SkillFrontmatter -Text $skillText
if ($skillText -match 'TODO|FIXME') {
    Fail 'SKILL.md still contains TODO/FIXME markers.'
}

$requiredSkillMarkers = @(
    'Not reviewable',
    'references/review-intake.md',
    'references/review-effort-signals.md',
    'references/heterogeneous-reviewers.md',
    'references/reviewer-prompts.md',
    'references/llm-security-review.md',
    'references/ci-gate-integrity.md',
    'references/batch-triage.md',
    'references/human-on-the-loop-audit.md',
    'references/team-adoption-metrics.md',
    'references/examples.md',
    'references/adoption.md',
    'diff measurement',
    'decision log',
    'AI review'
)

foreach ($marker in $requiredSkillMarkers) {
    if (-not $skillText.Contains($marker)) {
        Fail "SKILL.md missing required review workflow marker: $marker"
    }
}

$requiredRuntimeSupportMarkers = @(
    [pscustomobject]@{ RelativePath = 'README.md'; Pattern = 'Codex and Claude Code' },
    [pscustomobject]@{ RelativePath = 'README.md'; Pattern = 'Runtime Support' },
    [pscustomobject]@{ RelativePath = 'README.zh-CN.md'; Pattern = 'Codex.*Claude Code' },
    [pscustomobject]@{ RelativePath = 'scripts/install-local.ps1'; Pattern = 'ClaudeCode' },
    [pscustomobject]@{ RelativePath = 'scripts/install-local.ps1'; Pattern = 'CLAUDE_CONFIG_DIR' },
    [pscustomobject]@{ RelativePath = 'README.md'; Pattern = 'CLAUDE_CONFIG_DIR' },
    [pscustomobject]@{ RelativePath = 'README.zh-CN.md'; Pattern = 'CLAUDE_CONFIG_DIR' },
    [pscustomobject]@{ RelativePath = 'skills/agentic-code-review/SKILL.md'; Pattern = 'Codex and Claude Code' },
    [pscustomobject]@{ RelativePath = 'skills/agentic-code-review/assets/CLAUDE.snippet.md'; Pattern = 'CLAUDE\.md' },
    [pscustomobject]@{ RelativePath = 'skills/agentic-code-review/assets/CLAUDE.snippet.zh-CN.md'; Pattern = 'CLAUDE\.md' }
)

foreach ($marker in $requiredRuntimeSupportMarkers) {
    $path = Join-Path $repo $marker.RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Fail "Missing runtime support marker file: $($marker.RelativePath)"
    }
    $text = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    if ($text -notmatch $marker.Pattern) {
        Fail "Runtime support marker missing from $($marker.RelativePath): $($marker.Pattern)"
    }
}

$trackedSkillFiles = @($repositoryFiles | Where-Object { $_ -like 'skills/agentic-code-review/*' })
$skillPackageFiles = if ($trackedSkillFiles.Count -gt 0) {
    $trackedSkillFiles
}
else {
    foreach ($file in Get-ChildItem -LiteralPath $skill -Recurse -File -Force) {
        ($file.FullName.Substring($repoPrefix.Length) -replace '\\', '/')
    }
}

$blockedSkillPackagePatterns = @(
    '(^|/)__pycache__/',
    '(^|/)\.pytest_cache/',
    '(^|/)\.mypy_cache/',
    '(^|/)\.ruff_cache/',
    '\.pyc$',
    '\.pyo$',
    '\.log$'
)

foreach ($relative in $skillPackageFiles) {
    $normalizedRelative = $relative -replace '\\', '/'
    foreach ($pattern in $blockedSkillPackagePatterns) {
        if ($normalizedRelative -match $pattern) {
            Fail "Skill package includes generated or local-only artifact: $normalizedRelative"
        }
    }
}

$localizedMarkdownMap = [ordered]@{}
foreach ($relative in $localizedMarkdown) {
    $localizedMarkdownMap[$relative] = $true
}

foreach ($relative in $repositoryFiles) {
    if ($relative -notlike '*.md' -or $relative -like '*.zh-CN.md') {
        continue
    }
    $localizedMarkdownMap[$relative] = $true
}

$localizedMarkdown = @($localizedMarkdownMap.Keys)

foreach ($relative in $localizedMarkdown) {
    $englishPath = Join-Path $repo $relative
    if (-not (Test-Path -LiteralPath $englishPath -PathType Leaf)) {
        Fail "Missing localized English Markdown file: $relative"
    }

    $zhRelative = Get-ZhCnPath -RelativePath $relative
    $zhPath = Join-Path $repo $zhRelative
    if (-not (Test-Path -LiteralPath $zhPath -PathType Leaf)) {
        Fail "Missing Simplified Chinese companion Markdown file: $zhRelative"
    }

    $englishText = Get-Content -LiteralPath $englishPath -Raw -Encoding UTF8
    $zhText = Get-Content -LiteralPath $zhPath -Raw -Encoding UTF8
    if ($englishText -match '(?m)(^|\s)(EN|ZH):') {
        Fail "English Markdown still contains paired EN/ZH markers: $relative"
    }
    if ($englishText -match '[\p{IsCJKUnifiedIdeographs}]') {
        Fail "English Markdown still contains Simplified Chinese content: $relative"
    }
    if ($zhText -match '(?m)(^|\s)(EN|ZH):') {
        Fail "Simplified Chinese Markdown still contains paired EN/ZH markers: $zhRelative"
    }
    if ($zhText -notmatch '[\p{IsCJKUnifiedIdeographs}]') {
        Fail "Simplified Chinese Markdown appears to contain no Chinese text: $zhRelative"
    }

    $englishHeadingCount = Get-MarkdownHeadingCount -Text $englishText
    $zhHeadingCount = Get-MarkdownHeadingCount -Text $zhText
    if ($englishHeadingCount -ne $zhHeadingCount) {
        Fail "Localized Markdown heading count differs: $relative ($englishHeadingCount) vs $zhRelative ($zhHeadingCount)"
    }

    Assert-LocalizedMarkerParity -RelativePath $relative -ZhRelativePath $zhRelative -EnglishText $englishText -ZhText $zhText
}

$textExtensions = @('.md', '.yml', '.yaml', '.json', '.ps1', '.py', '.txt', '.csv')
$textFileNames = @('LICENSE', 'CODEOWNERS', '.editorconfig', '.gitattributes', '.gitignore')
$allTextFiles = foreach ($relative in $repositoryFiles) {
    $path = Join-Path $repo $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        continue
    }

    $file = Get-Item -LiteralPath $path
    $normalizedRelativePath = $relative -replace '\\', '/'
    if (
        ($file.Extension -in $textExtensions -or $file.Name -in $textFileNames)
    ) {
        [pscustomobject]@{
            File = $file
            RelativePath = $normalizedRelativePath
        }
    }
}

$blockedPathPatterns = @(
    ('D:' + '[/\\]+' + 'Work' + '[/\\]+' + 'Projects'),
    ('D:' + '[/\\]+' + 'Repositories'),
    ('C:' + '[/\\]+' + 'Users' + '[/\\]+' + 'liu liang')
)
$blockedArticleArtifact = 'agentic-code-review' + '.html'

foreach ($entry in $allTextFiles) {
    $file = $entry.File
    $relativePath = $entry.RelativePath
    $expectedLineEnding = if ($file.Extension -eq '.ps1') { 'CRLF' } else { 'LF' }
    Assert-LineEndings -Path $file.FullName -RelativePath $relativePath -ExpectedStyle $expectedLineEnding

    $text = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    foreach ($pattern in $blockedPathPatterns) {
        if ($text -match $pattern) {
            Fail "Local private path leaked into $relativePath"
        }
    }
    if ($text.Contains($blockedArticleArtifact)) {
        Fail "Downloaded source article artifact must not be referenced as repository content."
    }
}

function Assert-JsonFile {
    param([string]$RelativePath)

    $jsonPath = Join-Path $repo $RelativePath
    try {
        Get-Content -LiteralPath $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
    }
    catch {
        Fail "Invalid JSON: $RelativePath"
    }
}

foreach ($jsonRelative in @(
    'skills/agentic-code-review/assets/batch-triage.template.json',
    'skills/agentic-code-review/assets/batch-triage.schema.json',
    'skills/agentic-code-review/assets/forward-test-scenarios.json',
    'skills/agentic-code-review/assets/hostile-input-fixtures.json',
    'skills/agentic-code-review/assets/review-effort.config.example.json',
    'skills/agentic-code-review/assets/review-fix-loop.gates.example.json',
    'skills/agentic-code-review/assets/review-capacity-metrics.schema.json',
    'skills/agentic-code-review/assets/reviewer-comparison.example.json',
    'skills/agentic-code-review/assets/reviewer-comparison.schema.json'
)) {
    Assert-JsonFile -RelativePath $jsonRelative
}

$metricsCsvPath = Join-Path $skill 'assets/review-capacity-metrics.template.csv'
$metricsHeader = Get-Content -LiteralPath $metricsCsvPath -TotalCount 1 -Encoding UTF8
$requiredMetricColumns = @(
    'period_start',
    'period_end',
    'repository',
    'change_count',
    'zero_review_merges',
    'median_time_to_first_review_hours',
    'median_review_duration_hours',
    'median_files_changed',
    'median_changed_lines',
    'median_test_change_ratio',
    'not_reviewable_count',
    'gate_failure_count',
    'rereview_count',
    'valid_ai_findings',
    'false_positive_ai_findings',
    'reviewer_overlap_count',
    'agent_pr_abandonment_count',
    'notes'
)

foreach ($column in $requiredMetricColumns) {
    if (($metricsHeader -split ',') -notcontains $column) {
        Fail "Review capacity metrics template missing column: $column"
    }
}

Write-Host 'agentic-code-review-skill validation passed.'
