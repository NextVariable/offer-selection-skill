# Install the offer-selection-skill runtime package (Windows).
#
# Requires PowerShell 7+. CI and local verification exercise pwsh only; the
# installer is not claimed to support Windows PowerShell 5.1.
# Exit codes:
#   0 — Success
#   1 — Validation failed (missing or malformed SKILL.md)
#   2 — Platform not detected
#   3 — Permission denied

param(
    [string]$Platform = "",
    [switch]$Project,
    [string]$Path = "",
    [switch]$All,
    [switch]$DryRun,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
$SkillName = "offer-selection-skill"
$ScriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillDir = Join-Path $ScriptDir "skills\$SkillName"
$Manifest = Join-Path $ScriptDir ".claude-plugin\plugin.json"
$HomeDir = $env:USERPROFILE

function Get-RuntimeSource {
    param([string]$Entry)
    if ($Entry -in "SKILL.md", "references") { return Join-Path $SkillDir $Entry }
    return Join-Path $ScriptDir $Entry
}

# Ownership marker written into every install. Before overwriting an existing
# destination the installer requires a marker with exactly this schema/name, so
# a typo'd -Path can never delete a directory this installer did not create.
$MarkerName = ".offer-selection-skill-install.json"
$MarkerSchema = "offer-selection-skill-install/v1"

# Single source of truth for the version is .claude-plugin/plugin.json. This
# constant is only a last-resort fallback; a release check keeps it in sync.
$FallbackVersion = "0.3.2"

# Runtime allowlist - the ONLY things a normal user installation may receive.
# Anything not listed here (git metadata, audits, evals, archive, tools,
# workspace files, caches, and this repository's developer docs README/
# CONTRIBUTING/SECURITY/AGENTS) is development material and must never be
# shipped. SKILL.md is the installed usage entry point; developer docs live in
# the source repository. Add a new entry only when the runtime needs it.
$RuntimeAllowlist = @(
    "SKILL.md"
    "references"
    ".claude-plugin\plugin.json"
    ".claude-plugin\marketplace.json"
    "LICENSE"
)

# Files that must exist after staging for the skill to be runnable.
$RequiredRuntimeFiles = @(
    "SKILL.md"
    "references\core-decision-engine.md"
    "references\path-private-sector.md"
    "references\path-soe-public.md"
    "references\path-local-stay.md"
    "references\path-phd-academic.md"
    "references\priors-and-calibration.md"
)

# Directories that must never appear in an installation.
$ForbiddenDirs = @(".git", ".workbuddy", ".DS_Store", "internal", "audits", "evals",
                   "archive", "tools", "__pycache__")

# ---------------------------------------------------------------------------
# Version detection (manifest-first, verifiable fallback)
# ---------------------------------------------------------------------------
function Get-SkillVersion {
    $version = ""
    if (Test-Path -LiteralPath $Manifest) {
        try {
            $json = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
            $version = [string]$json.version
        } catch {
            $version = ""
        }
        if (-not $version) {
            # Text fallback: read the "version" field without a JSON parser.
            $m = [regex]::Match((Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8),
                                 '"version"\s*:\s*"([^"]+)"')
            if ($m.Success) { $version = $m.Groups[1].Value }
        }
    }
    if (-not $version) {
        $version = $FallbackVersion
        Write-Warn "Could not read the version from $Manifest; using fallback $version."
    }
    return $version
}

$Version = Get-SkillVersion

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
function Write-Info    { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Blue }
function Write-Ok      { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
if ($Help) {
    Write-Host @"
install.ps1 — Install the $SkillName skill (v$Version)

USAGE
    .\maintenance\install.ps1 [OPTIONS]

OPTIONS
    -Platform <name>   Explicit platform selection. One of:
                       claude-code, workbuddy, github-copilot, cursor, windsurf,
                       cline, codex, gemini, kiro, trae, goose,
                       opencode, roo-code, kilo-code, factory,
                       junie, antigravity, universal
    -Project           Install at project level (current directory)
    -Path <path>       Custom install path (overrides detection). Must be
                       absolute and end in '$SkillName'.
    -All               Install to ALL detected tool paths at once
    -DryRun            Show what would happen without making changes
    -Help              Show this help message

EXAMPLES
    .\maintenance\install.ps1                          # Auto-detect platform, user-level
    .\maintenance\install.ps1 -Project                 # Auto-detect platform, project-level
    .\maintenance\install.ps1 -Platform cursor         # Force Cursor, user-level
    .\maintenance\install.ps1 -Path C:\skills\$SkillName   # Custom destination
    .\maintenance\install.ps1 -All                     # Install to every detected tool
    .\maintenance\install.ps1 -DryRun                  # Preview without installing
"@
    exit 0
}

# ---------------------------------------------------------------------------
# SKILL.md validation
# ---------------------------------------------------------------------------
function Test-SkillMd {
    $skillMd = Join-Path $SkillDir "SKILL.md"

    if (-not (Test-Path $skillMd)) {
        Write-Err "SKILL.md not found in $SkillDir"
        Write-Err "Every skill package must contain a valid SKILL.md file."
        exit 1
    }

    $lines = Get-Content $skillMd -TotalCount 50
    if ($lines.Count -eq 0 -or $lines[0] -ne "---") {
        Write-Err "SKILL.md must start with YAML frontmatter (---)"
        exit 1
    }

    $foundName = $false
    $foundDesc = $false
    $inFrontmatter = $false

    foreach ($line in $lines) {
        if (-not $inFrontmatter -and $line -eq "---") {
            $inFrontmatter = $true
            continue
        }
        if ($inFrontmatter -and $line -eq "---") { break }
        if ($inFrontmatter) {
            if ($line -match "^name:") { $foundName = $true }
            if ($line -match "^description:") { $foundDesc = $true }
        }
    }

    if (-not $foundName) {
        Write-Err "SKILL.md frontmatter is missing required field: name"
        exit 1
    }
    if (-not $foundDesc) {
        Write-Err "SKILL.md frontmatter is missing required field: description"
        exit 1
    }

    Write-Ok "SKILL.md validated (name and description present)"
}

# ---------------------------------------------------------------------------
# Supported platforms
# ---------------------------------------------------------------------------
$SupportedPlatforms = @(
    "claude-code", "workbuddy", "github-copilot", "cursor", "windsurf", "cline", "codex",
    "gemini", "kiro", "trae", "goose", "opencode", "roo-code",
    "kilo-code", "factory", "junie", "antigravity", "universal"
)

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
function Find-Platform {
    if ($Platform) {
        if ($Platform -eq "copilot") {
            Write-Warn "Platform alias 'copilot' is deprecated; using 'github-copilot'."
            $Platform = "github-copilot"
        }
        if ($Platform -notin $SupportedPlatforms) {
            Write-Err "Unknown platform: $Platform"
            Write-Err "Supported: $($SupportedPlatforms -join ', ')"
            exit 2
        }
        Write-Info "Platform explicitly set to: $Platform"
        return $Platform
    }

    $checks = @(
        @{ Dir = ".claude";           Name = "claude-code" },
        @{ Dir = ".workbuddy\skills"; Name = "workbuddy" },
        @{ Dir = ".copilot";          Name = "github-copilot" },
        @{ Dir = ".cursor";           Name = "cursor" },
        @{ Dir = ".codeium\windsurf"; Name = "windsurf" },
        @{ Dir = ".cline";            Name = "cline" },
        @{ Dir = ".gemini";           Name = "gemini" },
        @{ Dir = ".kiro";             Name = "kiro" },
        @{ Dir = ".roo";              Name = "roo-code" },
        @{ Dir = ".kilocode";         Name = "kilo-code" },
        @{ Dir = ".factory";          Name = "factory" },
        @{ Dir = ".config\goose";     Name = "goose" },
        @{ Dir = ".config\opencode";  Name = "opencode" },
        @{ Dir = ".agents";           Name = "universal" }
    )

    # Also check project-level dirs. A `.github` directory is NOT a Copilot
    # signal — this repository itself ships one — so Copilot is detected only
    # via `~/.copilot` (VS Code extension) or the Copilot CLI config.
    $projectChecks = @(
        @{ Dir = ".cursor";    Name = "cursor" },
        @{ Dir = ".windsurf";  Name = "windsurf" },
        @{ Dir = ".clinerules"; Name = "cline" },
        @{ Dir = ".kiro";      Name = "kiro" },
        @{ Dir = ".trae";      Name = "trae" },
        @{ Dir = ".roo";       Name = "roo-code" },
        @{ Dir = ".kilocode";  Name = "kilo-code" },
        @{ Dir = ".factory";   Name = "factory" },
        @{ Dir = ".junie";     Name = "junie" }
    )

    foreach ($check in $checks) {
        $testPath = Join-Path $HomeDir $check.Dir
        if (Test-Path $testPath) {
            Write-Info "Auto-detected platform: $($check.Name)"
            return $check.Name
        }
    }

    foreach ($check in $projectChecks) {
        if (Test-Path $check.Dir) {
            Write-Info "Auto-detected platform: $($check.Name) (project-level)"
            return $check.Name
        }
    }

    Write-Err "Could not auto-detect any supported AI coding platform."
    Write-Err "Use -Platform <name> to specify one explicitly."
    Write-Err "Supported: $($SupportedPlatforms -join ', ')"
    exit 2
}

# ---------------------------------------------------------------------------
# Detect all installed platforms (for -All)
# ---------------------------------------------------------------------------
function Find-AllPlatforms {
    $found = @()

    $globalChecks = @(
        @{ Dir = ".claude";           Name = "claude-code" },
        @{ Dir = ".workbuddy\skills"; Name = "workbuddy" },
        @{ Dir = ".copilot";          Name = "github-copilot" },
        @{ Dir = ".cursor";           Name = "cursor" },
        @{ Dir = ".codeium\windsurf"; Name = "windsurf" },
        @{ Dir = ".cline";            Name = "cline" },
        @{ Dir = ".gemini";           Name = "gemini" },
        @{ Dir = ".kiro";             Name = "kiro" },
        @{ Dir = ".roo";              Name = "roo-code" },
        @{ Dir = ".kilocode";         Name = "kilo-code" },
        @{ Dir = ".factory";          Name = "factory" },
        @{ Dir = ".config\goose";     Name = "goose" },
        @{ Dir = ".config\opencode";  Name = "opencode" }
    )

    $projectChecks = @(
        @{ Dir = ".cursor";    Name = "cursor" },
        @{ Dir = ".windsurf";  Name = "windsurf" },
        @{ Dir = ".clinerules"; Name = "cline" },
        @{ Dir = ".kiro";      Name = "kiro" },
        @{ Dir = ".trae";      Name = "trae" },
        @{ Dir = ".roo";       Name = "roo-code" },
        @{ Dir = ".kilocode";  Name = "kilo-code" },
        @{ Dir = ".factory";   Name = "factory" },
        @{ Dir = ".junie";     Name = "junie" }
    )

    foreach ($check in $globalChecks) {
        $testPath = Join-Path $HomeDir $check.Dir
        if ((Test-Path $testPath) -and ($check.Name -notin $found)) {
            $found += $check.Name
        }
    }

    foreach ($check in $projectChecks) {
        if ((Test-Path $check.Dir) -and ($check.Name -notin $found)) {
            $found += $check.Name
        }
    }

    # Always include universal
    if ("universal" -notin $found) {
        $found += "universal"
    }

    return $found
}

# ---------------------------------------------------------------------------
# Install path resolution
# ---------------------------------------------------------------------------
function Resolve-InstallPath {
    param([string]$Plat)

    if ($Path) {
        # Expand a leading ~\ or ~/ to the user profile; otherwise the caller
        # must pass an absolute path (Assert-SafeInstallDir enforces it).
        $p = $Path.Trim()
        if ($p.StartsWith("~\")) { $p = Join-Path $HomeDir $p.Substring(2) }
        elseif ($p.StartsWith("~/")) { $p = Join-Path $HomeDir $p.Substring(2) }
        return $p
    }

    if ($Project) {
        $base = switch ($Plat) {
            "claude-code"   { ".claude\skills" }
            "workbuddy"     { ".workbuddy\skills" }
            "github-copilot" { ".github\skills" }
            "cursor"        { ".cursor\skills" }
            "windsurf"      { ".windsurf\skills" }
            "cline"         { ".clinerules\skills" }
            "codex"         { ".agents\skills" }
            "gemini"        { ".gemini\skills" }
            "kiro"          { ".kiro\skills" }
            "trae"          { ".trae\rules" }
            "goose"         { ".goose\skills" }
            "opencode"      { ".opencode\skills" }
            "roo-code"      { ".roo\skills" }
            "kilo-code"     { ".kilocode\skills" }
            "factory"       { ".factory\skills" }
            "junie"         { ".junie\skills" }
            "antigravity"   { ".agent\skills" }
            "universal"     { ".agents\skills" }
        }
        return Join-Path (Get-Location) $base $SkillName
    } else {
        $base = switch ($Plat) {
            "claude-code"   { Join-Path $HomeDir ".claude\skills" }
            "workbuddy"     { Join-Path $HomeDir ".workbuddy\skills" }
            "github-copilot" { Join-Path $HomeDir ".copilot\skills" }
            "cursor"        { Join-Path $HomeDir ".cursor\skills" }
            "windsurf"      { Join-Path $HomeDir ".codeium\windsurf\skills" }
            "cline"         { Join-Path $HomeDir ".cline\skills" }
            "codex"         { Join-Path $HomeDir ".agents\skills" }
            "gemini"        { Join-Path $HomeDir ".gemini\skills" }
            "kiro"          { Join-Path $HomeDir ".kiro\skills" }
            "trae"          { Join-Path $HomeDir ".trae\rules" }
            "goose"         { Join-Path $HomeDir ".config\goose\skills" }
            "opencode"      { Join-Path $HomeDir ".config\opencode\skills" }
            "roo-code"      { Join-Path $HomeDir ".roo\skills" }
            "kilo-code"     { Join-Path $HomeDir ".kilocode\skills" }
            "factory"       { Join-Path $HomeDir ".factory\skills" }
            "junie"         { Join-Path $HomeDir ".junie\skills" }
            "antigravity"   { Join-Path $HomeDir ".gemini\antigravity\skills" }
            "universal"     { Join-Path $HomeDir ".agents\skills" }
        }
        return Join-Path $base $SkillName
    }
}

# ---------------------------------------------------------------------------
# Platform display names
# ---------------------------------------------------------------------------
function Get-PlatformDisplay {
    param([string]$Plat)
    switch ($Plat) {
        "claude-code"   { "Claude Code" }
        "github-copilot" { "GitHub Copilot" }
        "cursor"        { "Cursor" }
        "windsurf"      { "Windsurf" }
        "cline"         { "Cline" }
        "codex"         { "Codex CLI" }
        "gemini"        { "Gemini CLI" }
        "kiro"          { "Kiro" }
        "trae"          { "Trae" }
        "goose"         { "Goose" }
        "opencode"      { "OpenCode" }
        "roo-code"      { "Roo Code" }
        "kilo-code"     { "Kilo Code" }
        "factory"       { "Factory Droid" }
        "junie"         { "Junie" }
        "antigravity"   { "Antigravity" }
        "universal"     { "Universal" }
        default         { $Plat }
    }
}

# Remove a path without ever following a reparse point into its target:
# symlinks/junctions are deleted as links only; real directories are removed
# recursively (callers must have verified ownership first).
function Remove-OwnedPath {
    param([string]$Path)
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        if ($item.PSIsContainer) { [System.IO.Directory]::Delete($Path) }
        else { [System.IO.File]::Delete($Path) }
        return
    }
    Remove-Item -LiteralPath $Path -Recurse -Force
}

# Create a directory junction (works without admin)
function New-SkillLink {
    param([string]$Target, [string]$LinkPath)

    if ($Target -eq $LinkPath) { return }

    $parentDir = Split-Path $LinkPath -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    if (Test-Path $LinkPath) {
        Remove-OwnedPath $LinkPath
    }

    # Try junction first (no admin), then symlink, then copy
    try {
        cmd /c mklink /J "`"$LinkPath`"" "`"$Target`"" 2>$null | Out-Null
        if (Test-Path $LinkPath) { return }
    } catch {}

    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $Target -Force | Out-Null
        if (Test-Path $LinkPath) { return }
    } catch {}

    Write-Warn "Junction/symlink failed for $LinkPath - falling back to copy"
    Copy-Item -Path $Target -Destination $LinkPath -Recurse -Force
}

# ---------------------------------------------------------------------------
# Extract SKILL.md body (everything after second ---)
# ---------------------------------------------------------------------------
function Get-SkillBody {
    $skillMd = Join-Path $SkillDir "SKILL.md"
    $lines = Get-Content $skillMd
    $delimCount = 0
    $bodyLines = @()

    foreach ($line in $lines) {
        if ($line -eq "---") {
            $delimCount++
            continue
        }
        if ($delimCount -ge 2) {
            $bodyLines += $line
        }
    }
    return ($bodyLines -join "`n")
}

# ---------------------------------------------------------------------------
# Extract description from SKILL.md frontmatter (handles folded YAML blocks)
# ---------------------------------------------------------------------------
function Get-SkillDescription {
    $skillMd = Join-Path $SkillDir "SKILL.md"
    $lines = Get-Content $skillMd
    $inFm = $false
    $got = $false
    $desc = ""

    foreach ($line in $lines) {
        if (-not $inFm -and $line -eq "---") { $inFm = $true; continue }
        if ($inFm -and $line -eq "---") { break }
        if ($inFm) {
            if (-not $got -and $line -match "^description:\s*(.*)$") {
                $got = $true
                $rest = $Matches[1].Trim()
                # A folded block (`>-` / `>`) means text continues on indented
                # following lines; the marker itself is not content.
                if ($rest -eq ">-" -or $rest -eq ">" -or $rest -eq "") {
                    $desc = ""
                } else {
                    $desc = $rest
                }
                continue
            }
            if ($got -and $line -match "^\s+(.*)$") {
                $part = $Matches[1].Trim()
                if ($desc -eq "") { $desc = $part } else { $desc = "$desc $part" }
                continue
            }
            if ($got) { break }
        }
    }
    return $desc
}

# ---------------------------------------------------------------------------
# Format adapters
# ---------------------------------------------------------------------------
function New-PlainRule {
    param([string]$TargetDir, [string]$FileName)

    $body = Get-SkillBody
    $plainFile = Join-Path $TargetDir $FileName

    if ($DryRun) {
        Write-Info "[dry-run] Would generate plain rule: $plainFile"
        return
    }

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    Set-Content -Path $plainFile -Value $body -Encoding UTF8
    Write-Ok "Generated plain rule: $plainFile"
}

function New-JunieGuideline {
    param([string]$TargetDir)

    $body = Get-SkillBody
    $guidelineFile = Join-Path $TargetDir "guidelines.md"

    if ($DryRun) {
        Write-Info "[dry-run] Would generate Junie guideline: $guidelineFile"
        return
    }

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    Set-Content -Path $guidelineFile -Value $body -Encoding UTF8
    Write-Ok "Generated Junie guideline: $guidelineFile"
}

function Invoke-Adapters {
    param([string]$Plat, [string]$InstallDir)

    switch ($Plat) {
        # Cursor and Windsurf discover the native SKILL.md package. Do not
        # flatten it into a rule and lose progressive disclosure/resources.
        { $_ -in "cursor", "windsurf" } { }
        { $_ -in "cline", "roo-code", "kilo-code", "trae" } {
            New-PlainRule $InstallDir "$SkillName.md"
        }
        "junie" { New-JunieGuideline $InstallDir }
    }
}

# ---------------------------------------------------------------------------
# AGENTS.md companion
# ---------------------------------------------------------------------------
function New-AgentsMd {
    param([string]$InstallDir)

    if (Test-Path (Join-Path $ScriptDir "AGENTS.md")) { return }
    if ($DryRun) {
        Write-Info "[dry-run] Would generate companion AGENTS.md"
        return
    }

    $desc = Get-SkillDescription
    $agentsMd = Join-Path $InstallDir "AGENTS.md"

    @"
# $SkillName

$desc

## Usage

Invoke this skill with ``/$SkillName`` or by describing a task that matches its description.

## Details

See [SKILL.md](./SKILL.md) for full implementation details, triggers, and configuration.
"@ | Set-Content -Path $agentsMd -Encoding UTF8
    Write-Ok "Generated companion AGENTS.md"
}

# ---------------------------------------------------------------------------
# Universal secondary install
# ---------------------------------------------------------------------------
function Install-UniversalSecondary {
    param([string]$Plat, [string]$InstallDir)

    # A custom path is an explicit containment boundary. Do not create a second
    # user-profile install that the caller did not request.
    if ($Path -or $Project) { return }

    if ($Plat -in "codex", "universal") { return }

    $universalDir = Join-Path $HomeDir ".agents\skills" $SkillName

    if ($DryRun) {
        Write-Info "[dry-run] Would create universal link: $universalDir -> $InstallDir"
        return
    }

    $parentDir = Split-Path $universalDir -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # Never let a secondary convenience link replace an existing universal or
    # Codex installation.
    if (Test-Path -LiteralPath $universalDir) {
        Write-Info "Universal skill path already exists; leaving it unchanged: $universalDir"
        return
    }

    New-SkillLink -Target $InstallDir -LinkPath $universalDir
    Write-Ok "Universal link: $universalDir -> $InstallDir"
}

# ---------------------------------------------------------------------------
# Destination safety + ownership marker
# ---------------------------------------------------------------------------
# Refuse to delete or overwrite anything that is not an explicit, strictly
# skill-shaped destination (see Assert-ManagedDestination for the overwrite
# contract).
function Assert-SafeInstallDir {
    param([string]$Dir)

    if ([string]::IsNullOrWhiteSpace($Dir) -or $Dir.Trim() -eq "/" -or $Dir.Trim() -eq "\") {
        Write-Err "Refusing to install to an unsafe destination: '$Dir'"
        exit 1
    }
    if (-not [System.IO.Path]::IsPathRooted($Dir)) {
        Write-Err "Install directory must be an absolute path: '$Dir'"
        Write-Err "For example: -Path C:\skills\$SkillName"
        exit 1
    }
    # Reject empty / '.' / '..' path components before any resolution so a
    # traversal-looking path cannot be resolved into a different directory.
    $norm = $Dir.TrimEnd('\', '/')
    foreach ($seg in $norm.Split(@('\', '/'))) {
        if ($seg -eq "" -or $seg -eq "." -or $seg -eq "..") {
            Write-Err "Refusing to install to '$Dir': it contains an empty, '.' or '..' path component."
            exit 1
        }
    }
    $full = [System.IO.Path]::GetFullPath($norm).TrimEnd('\', '/')
    if ($full -eq $HomeDir) {
        Write-Err "Refusing to install directly into your home directory: $HomeDir"
        Write-Err "Choose a dedicated skills directory (for example $HomeDir\.claude\skills)."
        exit 1
    }
    # The destination basename must be exactly the skill name. A typo'd -Path
    # that points at an arbitrary directory is rejected, not merely warned.
    if ((Split-Path $full -Leaf) -ne $SkillName) {
        Write-Err "Destination '$Dir' does not end in '$SkillName'."
        Write-Err "Refusing to install into a directory that is not a $SkillName install path."
        exit 1
    }
    if ($full -eq $ScriptDir -or $full -eq $SkillDir) {
        Write-Err "Refusing to install directly into the source package: $ScriptDir"
        exit 1
    }
    # Never allow the destination to be an ancestor of the source package.
    if ($ScriptDir.StartsWith($full + [System.IO.Path]::DirectorySeparatorChar,
            [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Err "Refusing to install into '$Dir': it contains the source package."
        exit 1
    }
}

# True if the file is a regular file carrying exactly our schema and skill name.
function Test-OwnershipMarker {
    param([string]$MarkerPath)
    if (-not (Test-Path -LiteralPath $MarkerPath -PathType Leaf)) { return $false }
    try {
        $item = Get-Item -LiteralPath $MarkerPath -Force
        if ($item.LinkType -or ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            return $false
        }
        $m = Get-Content -LiteralPath $MarkerPath -Raw -Encoding UTF8 | ConvertFrom-Json
        return ($m.schema -eq $MarkerSchema -and $m.name -eq $SkillName)
    } catch {
        return $false
    }
}

# True if every required runtime file exists under $Dir.
function Test-RuntimeFilesPresent {
    param([string]$Dir)
    foreach ($f in $RequiredRuntimeFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $Dir $f))) { return $false }
    }
    return $true
}

# Called before any overwrite (also in dry-run so the preview is accurate).
# A destination may be replaced only when it does not exist yet, carries a
# valid ownership marker (managed upgrade).
function Assert-ManagedDestination {
    param([string]$InstallDir)
    if (-not (Test-Path -LiteralPath $InstallDir)) { return }

    $item = Get-Item -LiteralPath $InstallDir -Force
    if ($item.LinkType -or ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        if (($Platform -in "codex", "universal") -and
            (Test-OwnershipMarker (Join-Path $InstallDir $MarkerName)) -and
            (Test-RuntimeFilesPresent $InstallDir)) {
            Write-Info "Migrating installer-managed universal link to a standalone install."
            if ($DryRun) { return }
            # Keep the link until staging succeeds; the swap backs up the link.
            return
        }
        Write-Err "Refusing to replace '$InstallDir': it is a symlink/junction."
        Write-Err "Remove the link yourself if you really want an install there."
        exit 1
    }
    if (-not (Test-Path -LiteralPath $InstallDir -PathType Container)) {
        Write-Err "Refusing to replace '$InstallDir': it exists and is not a directory."
        exit 1
    }

    $marker = Join-Path $InstallDir $MarkerName
    if (Test-Path -LiteralPath $marker) {
        if (Test-OwnershipMarker $marker) {
            Write-Info "Existing managed install detected at $InstallDir; upgrading in place."
            return
        }
        Write-Err "Refusing to overwrite '$InstallDir': its ownership marker is missing, unreadable, or does not match schema '$MarkerSchema' / name '$SkillName'."
        exit 1
    }

    Write-Err "Refusing to overwrite '$InstallDir': no valid installer ownership marker."
    Write-Err "Back up personal changes and remove the old copy with its original installation method, or choose a new destination."
    exit 1
}

# Write the ownership marker into a freshly staged package.
function New-OwnershipMarker {
    param([string]$StagingDir)
    $marker = Join-Path $StagingDir $MarkerName
    $obj = [ordered]@{
        schema  = $MarkerSchema
        name    = $SkillName
        version = $Version
    }
    $obj | ConvertTo-Json | Set-Content -LiteralPath $marker -Encoding UTF8
}

function Remove-Forbidden {
    param([string]$Root)
    foreach ($pat in @("__pycache__", ".git", ".workbuddy")) {
        Get-ChildItem -LiteralPath $Root -Recurse -Force -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq $pat } |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
    Get-ChildItem -LiteralPath $Root -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -in @(".DS_Store", ".env") -or $_.Extension -in @(".pyc", ".pyo") } |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

function Test-StagedRuntime {
    param([string]$StagingDir)

    foreach ($f in $RequiredRuntimeFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $StagingDir $f))) {
            Write-Err "Staged package is incomplete; missing: $f"
            exit 1
        }
    }
    foreach ($d in $ForbiddenDirs) {
        if (Test-Path -LiteralPath (Join-Path $StagingDir $d)) {
            Write-Err "Staged package contains forbidden directory: $d"
            exit 1
        }
    }
    if (-not (Test-OwnershipMarker (Join-Path $StagingDir $MarkerName))) {
        Write-Err "Staged package is missing a valid ownership marker ($MarkerName)."
        exit 1
    }
    Write-Ok "Verified SKILL.md and every runtime reference in the staged package"
}

function Install-Files {
    param([string]$InstallDir)

    # Path + ownership checks run in dry-run too, so an unsafe -Path fails
    # instead of being previewed as installable.
    Assert-SafeInstallDir $InstallDir
    Assert-ManagedDestination $InstallDir

    if ($DryRun) {
        Write-Host ""
        Write-Host "Dry-run mode - no files will be copied." -ForegroundColor White
        Write-Host ""
        Write-Info "Would create directory: $InstallDir"
        Write-Info "Runtime allowlist (the complete install payload):"
        foreach ($entry in $RuntimeAllowlist) {
            $src = Get-RuntimeSource $entry
            if (-not (Test-Path -LiteralPath $src)) {
                Write-Err "Would copy: $entry  (MISSING in the source package)"
                exit 1
            }
            Write-Info "Would copy: $entry"
        }
        Write-Info "Would write ownership marker: $MarkerName (schema $MarkerSchema)"
        Write-Host ""
        Write-Info "Never installed: $($ForbiddenDirs -join ', ')"
        Write-Info "Installer scripts and developer docs (README/CONTRIBUTING/SECURITY/AGENTS) are never copied."
        return ""
    }

    $parent = Split-Path -Parent $InstallDir
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $staging = Join-Path $parent ".$SkillName.staging.$PID"
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
    New-Item -ItemType Directory -Path $staging -Force | Out-Null

    try {
        foreach ($entry in $RuntimeAllowlist) {
            $src = Get-RuntimeSource $entry
            if (-not (Test-Path -LiteralPath $src)) {
                Write-Err "Runtime allowlist entry missing from the package: $entry"
                Write-Err "Refusing to install an incomplete skill package."
                exit 1
            }
            $dest = Join-Path $staging $entry
            $destParent = Split-Path -Parent $dest
            if (-not (Test-Path -LiteralPath $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            Copy-Item -LiteralPath $src -Destination $destParent -Recurse -Force
        }
        New-OwnershipMarker $staging
        Remove-Forbidden $staging
        Write-Ok "Staged the runtime allowlist + ownership marker"
    } catch {
        Write-Err "Failed to stage files: $($_.Exception.Message)"
        if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
        exit 3
    }

    return $staging
}

function Commit-StagedInstall {
    param([string]$StagingDir, [string]$InstallDir)

    $parent = Split-Path -Parent $InstallDir
    $old = Join-Path $parent ".$SkillName.previous.$PID"
    if (Test-Path -LiteralPath $old) {
        Remove-Item -LiteralPath $old -Recurse -Force
    }
    $movedOld = $false
    if (Test-Path -LiteralPath $InstallDir) {
        try {
            Move-Item -LiteralPath $InstallDir -Destination $old -Force
            $movedOld = $true
        } catch {
            Write-Err "Cannot move the existing install out of the way: $InstallDir"
            exit 3
        }
    }
    # Test-only fault injection, off by default and never set in normal use:
    # once the previous install is safely in backup, remove the staged copy so
    # the placement move below fails and the real restoration path runs. This
    # is the same code path a genuine placement failure would take.
    if ($env:OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP -eq "1") {
        Remove-Item -LiteralPath $StagingDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    try {
        Move-Item -LiteralPath $StagingDir -Destination $InstallDir -Force
        $stagingCommitted = $true
    } catch {
        # Placement failed. Report exactly what happened instead of claiming a
        # restoration that may not have happened. Three distinct states:
        #   A. a previous install existed and its automatic restore succeeded;
        #   B. a previous install existed but its automatic restore ALSO
        #      failed — the backup is kept (never deleted, never overwritten)
        #      and its exact path is printed so the user can restore manually;
        #   C. no previous install existed, so there was nothing to restore.
        if ($movedOld) {
            # Test-only fault injection, off by default and never set in normal
            # use: occupy the destination with a plain file so the restore move
            # below genuinely fails (a directory cannot replace a file) while
            # the backup directory is left intact. Only reachable after the old
            # install is safely in backup.
            if ($env:OFFER_SELECTION_INSTALLER_TEST_FAIL_RESTORE -eq "1") {
                New-Item -ItemType File -Path $InstallDir -Force -ErrorAction SilentlyContinue | Out-Null
            }
            try {
                Move-Item -LiteralPath $old -Destination $InstallDir -Force
                Write-Err "Failed to place the new install at $InstallDir."
                Write-Err "The previous install was restored successfully."
                exit 3
            } catch {
                Write-Err "Failed to place the new install at $InstallDir."
                Write-Err "Automatic restoration also failed."
                Write-Err "The previous install is preserved at $old."
                Write-Err "To restore it manually, run: Move-Item -LiteralPath '$old' -Destination '$InstallDir' -Force"
                exit 3
            }
        }
        Write-Err "Failed to place the new install at $InstallDir."
        Write-Err "No previous installation existed to restore."
        exit 3
    }
    if ($movedOld) {
        Remove-OwnedPath $old
    }
    Write-Ok "Installed $SkillName to $InstallDir"
}

# ---------------------------------------------------------------------------
# Install for a single platform
# ---------------------------------------------------------------------------
function Install-Single {
    $detectedPlatform = Find-Platform
    $installDir = Resolve-InstallPath $detectedPlatform
    Write-Info "Install directory: $installDir"

    $staging = Install-Files $installDir

    if ($DryRun) {
        # Adapters and companion file only report in dry-run mode.
        Invoke-Adapters $detectedPlatform $installDir
        New-AgentsMd $installDir
    } else {
        Invoke-Adapters $detectedPlatform $staging
        New-AgentsMd $staging
        Test-StagedRuntime $staging
        Commit-StagedInstall $staging $installDir
    }

    Install-UniversalSecondary $detectedPlatform $installDir

    if (-not $DryRun) {
        $display = Get-PlatformDisplay $detectedPlatform
        Write-Host ""
        Write-Host "Installation complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Installed for: $display"
        Write-Host "  Location: $installDir"
        Write-Host "  Invoke with: /$SkillName"
        Write-Host ""
    } else {
        Write-Info "Dry run complete. No changes were made."
    }
}

# ---------------------------------------------------------------------------
# Install for all detected platforms (-All)
# ---------------------------------------------------------------------------
function Install-All {
    if ($Path) {
        Write-Err "-Path cannot be combined with -All"
        exit 1
    }
    $platforms = Find-AllPlatforms
    Write-Info "Installing to all detected platforms: $($platforms -join ', ')"
    Write-Host "----------------------------------------"

    $count = 0
    $firstNonAgentsDir = ""

    foreach ($plat in $platforms) {
        Write-Host ""
        Write-Info "--- Installing for: $plat ---"
        $installDir = Resolve-InstallPath $plat
        Write-Info "Install directory: $installDir"

        $staging = Install-Files $installDir
        if ($DryRun) {
            Invoke-Adapters $plat $installDir
            New-AgentsMd $installDir
        } else {
            Invoke-Adapters $plat $staging
            New-AgentsMd $staging
            Test-StagedRuntime $staging
            Commit-StagedInstall $staging $installDir
        }
        $count++

        if (-not $firstNonAgentsDir -and $plat -notin "codex", "universal") {
            $firstNonAgentsDir = $installDir
        }
    }

    # Create universal link from first non-.agents/ install
    if ($firstNonAgentsDir) {
        Install-UniversalSecondary "placeholder" $firstNonAgentsDir
    }

    Write-Host ""
    if ($DryRun) {
        Write-Info "Dry run complete. No changes were made."
    } else {
        Write-Ok "Skill '$SkillName' installed to $count platform(s)."
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if ($Help) {
    Write-Host "install.ps1 - Install the $SkillName skill (v$Version)" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage:  ./install.ps1 [-Platform <name>] [-Project] [-Path <dir>] [-All] [-DryRun] [-Help]"
    Write-Host "The install payload is a fixed runtime allowlist: SKILL.md, references/,"
    Write-Host "references/priors-and-calibration.md, .claude-plugin/, LICENSE, and an"
    Write-Host "ownership marker (.offer-selection-skill-install.json)."
    Write-Host "Development material (audits, evals, archive, tools, .git) and the"
    Write-Host "developer docs (README/CONTRIBUTING/SECURITY/AGENTS) are never installed."
    exit 0
}

Write-Host "Installing skill: $SkillName (v$Version)" -ForegroundColor White
Write-Host "----------------------------------------"

Test-SkillMd

if ($All) {
    Install-All
} else {
    Install-Single
}

exit 0
