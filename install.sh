#!/bin/sh
# install-template.sh — Cross-platform skill installation script
# This file is a template. During skill generation, offer-selection-skill is replaced
# with the actual skill name and the result is shipped as install.sh inside
# every generated skill package.
#
# POSIX-compatible (works in bash, dash, zsh, ash, etc.)
# Exit codes:
#   0 — Success
#   1 — Validation failed (missing or malformed SKILL.md)
#   2 — Platform not detected
#   3 — Permission denied

set -eu

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILL_NAME="offer-selection-skill"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="${SCRIPT_DIR}/.claude-plugin/plugin.json"

# The single source of truth for the version is .claude-plugin/plugin.json.
# This constant is only a last-resort fallback for shells that can neither run
# python nor parse the manifest text; CI verifies that it matches the manifest.
FALLBACK_VERSION="0.3.2"

# Ownership marker written into every install. Before overwriting an existing
# destination the installer requires a marker with exactly this schema/name, so
# a typo'd --path can never delete a directory that this installer did not
# create (see assert_safe_install_dir + validate_existing_destination).
MARKER_NAME=".offer-selection-skill-install.json"
MARKER_SCHEMA="offer-selection-skill-install/v1"

# Runtime allowlist — the ONLY things a normal user installation may receive.
# Anything not listed here (git metadata, audits, evals, archive, tools,
# workspace files, caches, and this repository's developer docs README/
# CONTRIBUTING/SECURITY/AGENTS) is development material and must never be
# shipped. SKILL.md is the installed usage entry point; the developer-facing
# docs live in the source repository and would be broken-link clutter inside a
# runtime payload. Add a new entry only when the runtime actually needs it;
# never switch this to "copy everything except ...".
runtime_allowlist() {
    printf '%s\n' \
        "SKILL.md" \
        "references" \
        "domain/priors-and-calibration.md" \
        ".claude-plugin/plugin.json" \
        ".claude-plugin/marketplace.json" \
        "LICENSE"
}

# Files that must exist after staging for the skill to be runnable.
required_runtime_files() {
    printf '%s\n' \
        "SKILL.md" \
        "references/core-decision-engine.md" \
        "references/path-private-sector.md" \
        "references/path-soe-public.md" \
        "references/path-local-stay.md" \
        "references/path-phd-academic.md" \
        "domain/priors-and-calibration.md"
}

# Directories that must never appear in an installation.
FORBIDDEN_DIRS=".git .workbuddy .DS_Store audits evals archive tools __pycache__"

# ---------------------------------------------------------------------------
# Version detection (manifest-first, verifiable fallback)
# ---------------------------------------------------------------------------
detect_version() {
    VERSION=""

    if command -v python3 >/dev/null 2>&1; then
        VERSION="$(python3 - "$MANIFEST" <<'PY' 2>/dev/null || true
import json, sys
try:
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        print(json.load(fh).get("version", "").strip())
except Exception:
    print("")
PY
)"
    fi

    if [ -z "$VERSION" ] && command -v python >/dev/null 2>&1; then
        VERSION="$(python - "$MANIFEST" <<'PY' 2>/dev/null || true
import json, sys
try:
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        print(json.load(fh).get("version", "").strip())
except Exception:
    print("")
PY
)"
    fi

    # Text fallback: read the "version" field without a JSON parser.
    if [ -z "$VERSION" ] && [ -f "$MANIFEST" ]; then
        VERSION="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
            "$MANIFEST" 2>/dev/null | head -n 1 || true)"
    fi

    if [ -z "$VERSION" ]; then
        VERSION="$FALLBACK_VERSION"
        warn "Could not read the version from ${MANIFEST}; using fallback ${VERSION}."
    fi
}

# ---------------------------------------------------------------------------
# Colors (disabled when stdout is not a terminal)
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    NC=''
fi

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
info()    { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
error()   { printf "${RED}[ERROR]${NC} %s\n" "$1" >&2; }

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
show_help() {
    cat <<EOF
${BOLD}install.sh${NC} — Install the ${BOLD}${SKILL_NAME}${NC} skill (v${VERSION})

USAGE
    ./install.sh [OPTIONS]

OPTIONS
    --platform PLATFORM   Explicit platform selection. One of:
                          claude-code, workbuddy, github-copilot, cursor, windsurf,
                          cline, codex, gemini, kiro, trae, goose,
                          opencode, roo-code, kilo-code, factory,
                          junie, antigravity, universal
    --project             Install at project level (current directory)
    --path PATH           Custom install path (overrides detection). Must be
                          absolute and end in '${SKILL_NAME}'.
    --all                 Install to ALL detected tool paths at once
    --dry-run             Show what would happen without making changes
    -h, --help            Show this help message

EXAMPLES
    ./install.sh                          # Auto-detect platform, user-level
    ./install.sh --project                # Auto-detect platform, project-level
    ./install.sh --platform cursor        # Force Cursor, user-level
    ./install.sh --path ~/my-skills/offer-selection-skill  # Custom destination
    ./install.sh --all                    # Install to every detected tool
    ./install.sh --dry-run                # Preview without installing
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
PLATFORM=""
PROJECT_LEVEL=false
CUSTOM_PATH=""
DRY_RUN=false
INSTALL_ALL=false

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --platform)
                [ $# -ge 2 ] || { error "Missing value for --platform"; exit 1; }
                PLATFORM="$2"
                shift 2
                ;;
            --project)
                PROJECT_LEVEL=true
                shift
                ;;
            --path)
                [ $# -ge 2 ] || { error "Missing value for --path"; exit 1; }
                CUSTOM_PATH="$2"
                shift 2
                ;;
            --all)
                INSTALL_ALL=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# SKILL.md validation
# ---------------------------------------------------------------------------
validate_skill_md() {
    skill_md="${SCRIPT_DIR}/SKILL.md"

    if [ ! -f "$skill_md" ]; then
        error "SKILL.md not found in ${SCRIPT_DIR}"
        error "Every skill package must contain a valid SKILL.md file."
        exit 1
    fi

    # Check that the file starts with YAML frontmatter delimiter
    first_line="$(head -n 1 "$skill_md")"
    if [ "$first_line" != "---" ]; then
        error "SKILL.md must start with YAML frontmatter (---)"
        exit 1
    fi

    # Verify required frontmatter fields: name and description
    in_frontmatter=false
    found_name=false
    found_description=false
    line_num=0

    while IFS= read -r line; do
        line_num=$((line_num + 1))

        if [ "$line_num" -eq 1 ]; then
            in_frontmatter=true
            continue
        fi

        if $in_frontmatter && [ "$line" = "---" ]; then
            break
        fi

        if $in_frontmatter; then
            case "$line" in
                name:*) found_name=true ;;
                description:*) found_description=true ;;
            esac
        fi
    done < "$skill_md"

    if ! $found_name; then
        error "SKILL.md frontmatter is missing required field: name"
        exit 1
    fi

    if ! $found_description; then
        error "SKILL.md frontmatter is missing required field: description"
        exit 1
    fi

    success "SKILL.md validated (name and description present)"
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
SUPPORTED_PLATFORMS="codex, workbuddy, claude-code, github-copilot, cursor, windsurf, cline, gemini, kiro, trae, goose, opencode, roo-code, kilo-code, factory, junie, antigravity, universal"

detect_platform() {
    # If explicitly provided, validate and return it.
    if [ -n "$PLATFORM" ]; then
        if [ "$PLATFORM" = "copilot" ]; then
            warn "Platform alias 'copilot' is deprecated; using 'github-copilot'."
            PLATFORM="github-copilot"
        fi
        case "$PLATFORM" in
            claude-code|workbuddy|github-copilot|cursor|windsurf|cline|codex|gemini|\
            kiro|trae|goose|opencode|roo-code|kilo-code|factory|\
            junie|antigravity|universal)
                info "Platform explicitly set to: ${PLATFORM}"
                return 0
                ;;
            *)
                error "Unknown platform: ${PLATFORM}"
                error "Supported: ${SUPPORTED_PLATFORMS}"
                exit 2
                ;;
        esac
    fi

    # Auto-detection: check user-level config directories.
    # Order matters — check most specific / least ambiguous first.
    # Detection is based on real client config directories only. A `.github`
    # directory is NOT a Copilot signal — this repository itself ships one — so
    # Copilot is detected only via `~/.copilot` (VS Code extension) or the
    # Copilot CLI config.
    if [ -d "${HOME}/.claude" ]; then
        PLATFORM="claude-code"
    elif [ -d "${HOME}/.workbuddy/skills" ]; then
        PLATFORM="workbuddy"
    elif [ -d "${HOME}/.copilot" ] || [ -d "${HOME}/.config/github-copilot" ]; then
        PLATFORM="github-copilot"
    elif [ -d "${HOME}/.cursor" ] || [ -d ".cursor" ]; then
        PLATFORM="cursor"
    elif [ -d "${HOME}/.codeium/windsurf" ] || [ -d ".windsurf" ]; then
        PLATFORM="windsurf"
    elif [ -d "${HOME}/.cline" ] || [ -d ".clinerules" ]; then
        PLATFORM="cline"
    elif [ -d "${HOME}/.gemini" ]; then
        PLATFORM="gemini"
    elif [ -d "${HOME}/.kiro" ] || [ -d ".kiro" ]; then
        PLATFORM="kiro"
    elif [ -d ".trae" ]; then
        PLATFORM="trae"
    elif [ -d "${HOME}/.roo" ] || [ -d ".roo" ]; then
        PLATFORM="roo-code"
    elif [ -d "${HOME}/.kilocode" ] || [ -d ".kilocode" ]; then
        PLATFORM="kilo-code"
    elif [ -d "${HOME}/.factory" ] || [ -d ".factory" ]; then
        PLATFORM="factory"
    elif [ -d ".junie" ]; then
        PLATFORM="junie"
    elif [ -d "${HOME}/.config/goose" ]; then
        PLATFORM="goose"
    elif [ -d "${HOME}/.config/opencode" ]; then
        PLATFORM="opencode"
    elif [ -d "${HOME}/.agents" ]; then
        PLATFORM="universal"
    else
        error "Could not auto-detect any supported AI coding platform."
        error "Use --platform PLATFORM to specify one explicitly."
        error "Supported: ${SUPPORTED_PLATFORMS}"
        exit 2
    fi

    info "Auto-detected platform: ${PLATFORM}"
}

# ---------------------------------------------------------------------------
# Detect all installed platforms (for --all)
# ---------------------------------------------------------------------------
detect_all_platforms() {
    ALL_PLATFORMS=""
    if [ -d "${HOME}/.claude" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} claude-code"
    fi
    if [ -d "${HOME}/.workbuddy/skills" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} workbuddy"
    fi
    if [ -d "${HOME}/.copilot" ] || [ -d "${HOME}/.config/github-copilot" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} github-copilot"
    fi
    if [ -d "${HOME}/.cursor" ] || [ -d ".cursor" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} cursor"
    fi
    if [ -d "${HOME}/.codeium/windsurf" ] || [ -d ".windsurf" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} windsurf"
    fi
    if [ -d "${HOME}/.cline" ] || [ -d ".clinerules" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} cline"
    fi
    if [ -d "${HOME}/.gemini" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} gemini"
    fi
    if [ -d "${HOME}/.kiro" ] || [ -d ".kiro" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} kiro"
    fi
    if [ -d ".trae" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} trae"
    fi
    if [ -d "${HOME}/.roo" ] || [ -d ".roo" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} roo-code"
    fi
    if [ -d "${HOME}/.kilocode" ] || [ -d ".kilocode" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} kilo-code"
    fi
    if [ -d "${HOME}/.factory" ] || [ -d ".factory" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} factory"
    fi
    if [ -d ".junie" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} junie"
    fi
    if [ -d "${HOME}/.config/goose" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} goose"
    fi
    if [ -d "${HOME}/.config/opencode" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} opencode"
    fi
    # Always include universal
    ALL_PLATFORMS="${ALL_PLATFORMS} universal"

    # Trim leading space
    ALL_PLATFORMS="$(printf '%s' "$ALL_PLATFORMS" | sed 's/^ //')"

    if [ -z "$ALL_PLATFORMS" ]; then
        ALL_PLATFORMS="universal"
    fi
}

# ---------------------------------------------------------------------------
# Install path resolution
# ---------------------------------------------------------------------------
# Sets INSTALL_DIR based on platform, project-level flag, or custom path.
resolve_install_path() {
    # Custom path takes precedence over everything. It must be absolute (a
    # leading ~/ is expanded to $HOME); the basename must equal the skill name
    # and is enforced in assert_safe_install_dir.
    if [ -n "$CUSTOM_PATH" ]; then
        case "$CUSTOM_PATH" in
            '~/'*)
                # Quote the pattern so the shell's tilde expansion cannot
                # swallow absolute paths in `case` matching.
                INSTALL_DIR="${HOME}/${CUSTOM_PATH#\~/}"
                ;;
            /*)
                INSTALL_DIR="${CUSTOM_PATH}"
                ;;
            *)
                error "Custom path must be absolute: '${CUSTOM_PATH}'"
                error "For example: --path \"/absolute/path/to/${SKILL_NAME}\""
                exit 1
                ;;
        esac
        # Strip any trailing slashes (never a bare "/" afterwards).
        while [ "${INSTALL_DIR}" != "/" ] && [ -z "${INSTALL_DIR##*/}" ]; do
            INSTALL_DIR="${INSTALL_DIR%/}"
        done
        info "Using custom install path: ${INSTALL_DIR}"
        return 0
    fi

    base=""

    if $PROJECT_LEVEL; then
        # Project-level: paths are relative to the current working directory.
        case "$PLATFORM" in
            claude-code)   base=".claude/skills" ;;
            workbuddy)     base=".workbuddy/skills" ;;
            github-copilot) base=".github/skills" ;;
            cursor)        base=".cursor/skills" ;;
            windsurf)      base=".windsurf/skills" ;;
            cline)         base=".clinerules/skills" ;;
            codex)         base=".agents/skills" ;;
            gemini)        base=".gemini/skills" ;;
            kiro)          base=".kiro/skills" ;;
            trae)          base=".trae/rules" ;;
            goose)         base=".goose/skills" ;;
            opencode)      base=".opencode/skills" ;;
            roo-code)      base=".roo/skills" ;;
            kilo-code)     base=".kilocode/skills" ;;
            factory)       base=".factory/skills" ;;
            junie)         base=".junie/skills" ;;
            antigravity)   base=".agent/skills" ;;
            universal)     base=".agents/skills" ;;
        esac
        INSTALL_DIR="$(pwd)/${base}/${SKILL_NAME}"
    else
        # User-level: paths are under the home directory.
        case "$PLATFORM" in
            claude-code)   base="${HOME}/.claude/skills" ;;
            workbuddy)     base="${HOME}/.workbuddy/skills" ;;
            github-copilot) base="${HOME}/.copilot/skills" ;;
            cursor)        base="${HOME}/.cursor/skills" ;;
            windsurf)      base="${HOME}/.codeium/windsurf/skills" ;;
            cline)         base="${HOME}/.cline/skills" ;;
            codex)         base="${HOME}/.agents/skills" ;;
            gemini)        base="${HOME}/.gemini/skills" ;;
            kiro)          base="${HOME}/.kiro/skills" ;;
            trae)          base="${HOME}/.trae/rules" ;;
            goose)         base="${HOME}/.config/goose/skills" ;;
            opencode)      base="${HOME}/.config/opencode/skills" ;;
            roo-code)      base="${HOME}/.roo/skills" ;;
            kilo-code)     base="${HOME}/.kilocode/skills" ;;
            factory)       base="${HOME}/.factory/skills" ;;
            junie)         base="${HOME}/.junie/skills" ;;
            antigravity)   base="${HOME}/.gemini/antigravity/skills" ;;
            universal)     base="${HOME}/.agents/skills" ;;
        esac
        INSTALL_DIR="${base}/${SKILL_NAME}"
    fi

    info "Install directory: ${INSTALL_DIR}"
}

# ---------------------------------------------------------------------------
# Format adapters — convert SKILL.md to platform-native formats
# ---------------------------------------------------------------------------

# Extract the SKILL.md frontmatter `description` as a single line. Handles both
# a single-line value and a YAML folded block (`description: >-` followed by
# indented lines), which is the format this repository ships. Returns via echo.
extract_skill_description() {
    skill_md="${SCRIPT_DIR}/SKILL.md"
    # awk: after the first `---`, collect `description:` and any continuation
    # lines that are more-indented than the key. Fold them into one line.
    awk '
        BEGIN { infm = 0; got = 0; desc = "" }
        NR == 1 { infm = 1; next }
        infm && $0 == "---" { exit }
        infm {
            if (!got && $0 ~ /^description:/) {
                got = 1
                rest = $0
                sub(/^description:[ \t]*/, "", rest)
                # A folded block: `>-` or `>` marker means the text continues on
                # indented following lines; the marker itself is not content.
                if (rest == ">-" || rest == ">" || rest == "") {
                    desc = ""
                } else {
                    desc = rest
                }
                next
            }
            if (got && $0 ~ /^[ \t]+/) {
                line = $0
                sub(/^[ \t]+/, "", line)
                if (desc == "") { desc = line } else { desc = desc " " line }
                next
            }
            if (got) { exit }
        }
        END { print desc }
    ' "$skill_md"
}

# Generate plain markdown (strip YAML frontmatter) for Cline/Roo/Trae/Kilo
generate_plain_rule() {
    target_dir="$1"
    filename="$2"
    skill_md="${SCRIPT_DIR}/SKILL.md"

    plain_file="${target_dir}/${filename}"

    if $DRY_RUN; then
        info "Would generate plain rule: ${plain_file}"
        return 0
    fi

    mkdir -p "$target_dir"
    awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md" > "$plain_file"
    success "Generated plain rule: ${plain_file}"
}

# Generate Junie guidelines.md (plain body, no frontmatter)
generate_junie_guideline() {
    target_dir="$1"
    skill_md="${SCRIPT_DIR}/SKILL.md"

    guideline_file="${target_dir}/guidelines.md"

    if $DRY_RUN; then
        info "Would generate Junie guideline: ${guideline_file}"
        return 0
    fi

    mkdir -p "$target_dir"
    awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md" > "$guideline_file"
    success "Generated Junie guideline: ${guideline_file}"
}

# ---------------------------------------------------------------------------
# AGENTS.md companion — generate if not already present in source
# ---------------------------------------------------------------------------
generate_agents_md() {
    # Generated into the staging directory so an aborted install never leaves a
    # half-written destination behind.
    target="${WORK_DIR:-$INSTALL_DIR}"
    agents_md="${target}/AGENTS.md"

    # If the skill already ships an AGENTS.md, skip generation
    if [ -f "${SCRIPT_DIR}/AGENTS.md" ]; then
        return 0
    fi

    if $DRY_RUN; then
        info "Would generate companion AGENTS.md"
        return 0
    fi

    desc="$(extract_skill_description)"

    cat > "$agents_md" <<AGENTSEOF
# ${SKILL_NAME}

${desc}

## Usage

Invoke this skill with \`/${SKILL_NAME}\` or by describing a task that matches its description.

## Details

See [SKILL.md](./SKILL.md) for full implementation details, triggers, and configuration.
AGENTSEOF
    success "Generated companion AGENTS.md"
}

# ---------------------------------------------------------------------------
# Universal .agents/skills/ secondary install (symlink or copy)
# ---------------------------------------------------------------------------
install_universal_secondary() {
    # A custom path is an explicit containment boundary. Do not create a second
    # user-home install that the caller did not request.
    [ -n "$CUSTOM_PATH" ] && return 0

    # Skip if primary target is already .agents/
    case "$PLATFORM" in
        codex|universal) return 0 ;;
    esac

    universal_dir="${HOME}/.agents/skills/${SKILL_NAME}"

    if $DRY_RUN; then
        info "Would create universal symlink: ${universal_dir} -> ${INSTALL_DIR}"
        return 0
    fi

    mkdir -p "${HOME}/.agents/skills"

    # A universal install may already be the user's real Codex installation or
    # a link created for another host. Never let a secondary convenience link
    # replace it; all copies carry the same runtime package anyway.
    if [ -e "$universal_dir" ] || [ -L "$universal_dir" ]; then
        info "Universal skill path already exists; leaving it unchanged: ${universal_dir}"
        return 0
    fi

    # Try symlink first, fallback to copy
    if ln -s "$INSTALL_DIR" "$universal_dir" 2>/dev/null; then
        success "Universal symlink: ${universal_dir} -> ${INSTALL_DIR}"
    elif cp -R "$INSTALL_DIR" "$universal_dir" 2>/dev/null; then
        success "Universal copy: ${universal_dir}"
    else
        warn "Could not create universal path at ${universal_dir}"
    fi
}

# ---------------------------------------------------------------------------
# Destination safety
# ---------------------------------------------------------------------------
# Refuse to delete or overwrite anything that is not an explicit, strictly
# skill-shaped destination. The installer may only ever remove
# <somewhere>/offer-selection-skill and, even then, only after the directory
# has proven it is owned by this installer (or satisfies the legacy contract —
# see validate_existing_destination).
assert_safe_install_dir() {
    case "$INSTALL_DIR" in
        ""|"/"|"."|".."|"/.")
            error "Refusing to install to an unsafe destination: '${INSTALL_DIR}'"
            exit 1
            ;;
    esac
    case "$INSTALL_DIR" in
        /*) : ;;
        *)  error "Install directory must be an absolute path: '${INSTALL_DIR}'"
            exit 1
            ;;
    esac
    # Reject empty/./.. path components (e.g. a//b or /a/../b). Splitting the
    # absolute path on "/" must yield only real directory names.
    _bad_component=""
    IFS='/'
    for _part in ${INSTALL_DIR#/}; do
        case "$_part" in
            ""|"."|"..") _bad_component="$_part" ; break ;;
        esac
    done
    unset IFS
    if [ -n "$_bad_component" ]; then
        error "Refusing to install to '${INSTALL_DIR}': it contains an empty, '.' or '..' path component."
        exit 1
    fi
    if [ "$INSTALL_DIR" = "${HOME:-/nonexistent}" ]; then
        error "Refusing to install directly into your home directory: ${HOME}"
        error "Choose a dedicated skills directory (for example ~/.claude/skills)."
        exit 1
    fi
    # The destination basename must be exactly the skill name. A typo'd --path
    # that points at an arbitrary directory is rejected, not merely warned.
    if [ "$(basename "$INSTALL_DIR")" != "$SKILL_NAME" ]; then
        error "Destination '${INSTALL_DIR}' does not end in '${SKILL_NAME}'."
        error "Refusing to install into a directory that is not a ${SKILL_NAME} install path."
        exit 1
    fi
    if [ "$INSTALL_DIR" = "$SCRIPT_DIR" ]; then
        error "Refusing to install directly into the source package: ${SCRIPT_DIR}"
        exit 1
    fi
    # Never allow the destination to be an ancestor of the source package:
    # replacing it could delete the package we are installing from.
    case "${SCRIPT_DIR}/" in
        "${INSTALL_DIR}/"*)
            error "Refusing to install into '${INSTALL_DIR}': it contains the source package."
            exit 1
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Ownership marker + managed-destination validation
# ---------------------------------------------------------------------------
# True if the file is a regular file carrying exactly our schema and skill name.
marker_matches() {
    marker_file="$1"
    if [ -L "$marker_file" ] || [ ! -f "$marker_file" ]; then
        return 1
    fi
    if command -v python3 >/dev/null 2>&1; then
        if python3 - "$marker_file" "$MARKER_SCHEMA" "$SKILL_NAME" <<'PY' 2>/dev/null
import json, sys
try:
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        data = json.load(fh)
except Exception:
    sys.exit(1)
sys.exit(0 if data.get("schema") == sys.argv[2] and data.get("name") == sys.argv[3] else 1)
PY
        then
            return 0
        fi
        return 1
    fi
    # No JSON parser available: verify the two governing fields literally.
    if grep -q "\"schema\"[[:space:]]*:[[:space:]]*\"${MARKER_SCHEMA}\"" "$marker_file" 2>/dev/null &&
       grep -q "\"name\"[[:space:]]*:[[:space:]]*\"${SKILL_NAME}\"" "$marker_file" 2>/dev/null; then
        return 0
    fi
    return 1
}

# True if $1/SKILL.md has frontmatter `name: <expected>` exactly.
frontmatter_name_is() {
    skill_file="$1"
    expected="$2"
    [ -f "$skill_file" ] || return 1
    awk -v want="$expected" '
        NR == 1 && $0 == "---" { in_fm = 1; next }
        in_fm && $0 == "---"   { exit }
        in_fm && $0 ~ /^name:/ {
            line = $0
            sub(/^name:[ \t]*/, "", line)
            sub(/[ \t\r]+$/, "", line)
            if (line == want) found = 1
        }
        END { exit (found ? 0 : 1) }
    ' "$skill_file"
}

# True if every runtime file exists under $1.
has_all_runtime_files() {
    root_dir="$1"
    for f in $(required_runtime_files); do
        [ -f "${root_dir}/${f}" ] || return 1
    done
    return 0
}

# Called before any overwrite. A destination may be replaced only when:
#   - it does not exist yet (fresh install), or
#   - it carries a valid ownership marker (managed upgrade), or
#   - it satisfies the legacy contract for installs made before markers
#     existed (basename + SKILL.md name + every runtime reference), in which
#     case the replacement writes the marker and the user is told.
# Anything else is refused untouched.
validate_existing_destination() {
    if [ ! -e "$INSTALL_DIR" ] && [ ! -L "$INSTALL_DIR" ]; then
        return 0  # fresh install
    fi
    if [ -L "$INSTALL_DIR" ]; then
        # A prior non-Codex install may have created this universal link. When
        # it resolves to a marker-managed copy of this exact skill, a direct
        # Codex/universal install may safely replace the link itself (never its
        # target) with a standalone managed installation.
        case "$PLATFORM" in
            codex|universal)
                if marker_matches "${INSTALL_DIR}/${MARKER_NAME}" &&
                   has_all_runtime_files "$INSTALL_DIR"; then
                    info "Migrating installer-managed universal link to a standalone install."
                    $DRY_RUN && return 0
                    rm -f "$INSTALL_DIR"
                    return 0
                fi
                ;;
        esac
        error "Refusing to replace '${INSTALL_DIR}': it is a symlink."
        error "Remove the symlink yourself if you really want an install there."
        exit 1
    fi
    if [ ! -d "$INSTALL_DIR" ]; then
        error "Refusing to replace '${INSTALL_DIR}': it exists and is not a directory."
        exit 1
    fi

    marker="${INSTALL_DIR}/${MARKER_NAME}"
    if [ -e "$marker" ] || [ -L "$marker" ]; then
        if marker_matches "$marker"; then
            info "Existing managed install detected at ${INSTALL_DIR}; upgrading in place."
            return 0
        fi
        error "Refusing to overwrite '${INSTALL_DIR}': its ownership marker is missing, unreadable, or does not match schema '${MARKER_SCHEMA}' / name '${SKILL_NAME}'."
        exit 1
    fi

    # Legacy migration: a pre-marker install made by an older version of this
    # installer. Only accept it when the directory is provably skill-shaped.
    if frontmatter_name_is "${INSTALL_DIR}/SKILL.md" "$SKILL_NAME" &&
       has_all_runtime_files "$INSTALL_DIR"; then
        warn "Existing install at ${INSTALL_DIR} has no ownership marker but matches the legacy install contract."
        warn "Migrating it to a marker-managed install."
        return 0
    fi
    error "Refusing to overwrite '${INSTALL_DIR}': it exists but is not a directory managed by this installer (no valid ownership marker, and no matching legacy skill layout)."
    error "Choose a different destination or remove the directory yourself."
    exit 1
}

# Write the ownership marker into a freshly staged package.
write_marker() {
    dest_dir="$1"
    cat > "${dest_dir}/${MARKER_NAME}" <<EOF
{
  "schema": "${MARKER_SCHEMA}",
  "name": "${SKILL_NAME}",
  "version": "${VERSION}"
}
EOF
}

# ---------------------------------------------------------------------------
# Staging (build in a temp dir next to the destination, then atomically swap)
# ---------------------------------------------------------------------------
STAGING_DIR=""
STAGING_SEQ=0

cleanup() {
    if [ -n "${STAGING_DIR:-}" ] && [ -d "${STAGING_DIR:-}" ]; then
        rm -rf "$STAGING_DIR" 2>/dev/null || true
    fi
    return 0
}

prepare_staging() {
    parent="$(dirname "$INSTALL_DIR")"
    STAGING_SEQ=$((STAGING_SEQ + 1))
    STAGING_DIR="${parent}/.${SKILL_NAME}.staging.$$-${STAGING_SEQ}"
    rm -rf "$STAGING_DIR" 2>/dev/null || true
    if ! mkdir -p "$STAGING_DIR" 2>/dev/null; then
        error "Cannot create a staging directory under: ${parent}"
        error "Check file permissions or run with appropriate privileges."
        exit 3
    fi
}

# ---------------------------------------------------------------------------
# File installation (strict allowlist)
# ---------------------------------------------------------------------------
prune_forbidden() {
    # Safety net only: the allowlist is the real guarantee. This removes
    # machine-local noise that could otherwise ride along inside a copied dir.
    if [ -d "$STAGING_DIR" ]; then
        find "$STAGING_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
        find "$STAGING_DIR" -type f \( -name '.DS_Store' -o -name '*.pyc' -o -name '*.pyo' \
            -o -name '.env' \) -exec rm -f {} + 2>/dev/null || true
    fi
    return 0
}

stage_runtime_files() {
    count=0
    for entry in $(runtime_allowlist); do
        src="${SCRIPT_DIR}/${entry}"
        if [ ! -e "$src" ]; then
            error "Runtime allowlist entry missing from the package: ${entry}"
            error "Refusing to install an incomplete skill package."
            exit 1
        fi
        dest="${STAGING_DIR}/${entry}"
        mkdir -p "$(dirname "$dest")"
        if ! cp -R "$src" "$dest" 2>/dev/null; then
            error "Failed to copy ${entry} into the staging directory."
            error "Check file permissions."
            exit 3
        fi
        count=$((count + 1))
    done
    write_marker "$STAGING_DIR"
    prune_forbidden
    success "Staged ${count} runtime entr(y/ies) + ownership marker"
}

verify_staged_runtime() {
    missing=""
    for f in $(required_runtime_files); do
        [ -f "${STAGING_DIR}/${f}" ] || missing="${missing} ${f}"
    done
    if [ -n "$missing" ]; then
        error "Staged package is incomplete; missing:${missing}"
        exit 1
    fi
    for d in ${FORBIDDEN_DIRS}; do
        if [ -e "${STAGING_DIR}/${d}" ]; then
            error "Staged package contains forbidden directory: ${d}"
            exit 1
        fi
    done
    if [ -d "${STAGING_DIR}/.git" ] || [ -d "${STAGING_DIR}/.workbuddy" ]; then
        error "Staged package contains machine-local metadata (.git/.workbuddy)."
        exit 1
    fi
    if [ -f "${STAGING_DIR}/${MARKER_NAME}" ] && marker_matches "${STAGING_DIR}/${MARKER_NAME}"; then
        :  # ownership marker present and valid
    else
        error "Staged package is missing a valid ownership marker (${MARKER_NAME})."
        exit 1
    fi
    success "Verified SKILL.md and every runtime reference in the staged package"
}

commit_staged_install() {
    parent="$(dirname "$INSTALL_DIR")"
    old="${parent}/.${SKILL_NAME}.previous.$$"
    rm -rf "$old" 2>/dev/null || true
    moved_old=false
    if [ -e "$INSTALL_DIR" ] || [ -L "$INSTALL_DIR" ]; then
        if ! mv "$INSTALL_DIR" "$old" 2>/dev/null; then
            error "Cannot move the existing install out of the way: ${INSTALL_DIR}"
            exit 3
        fi
        moved_old=true
    fi
    # Test-only fault injection, off by default and never set in normal use:
    # once the previous install is safely in backup, remove the staged copy so
    # the placement move below fails and the real restoration path runs. This
    # is the same code path a genuine placement failure would take.
    if [ "${OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP:-0}" = "1" ]; then
        rm -rf "$STAGING_DIR" 2>/dev/null || true
    fi
    if ! mv "$STAGING_DIR" "$INSTALL_DIR" 2>/dev/null; then
        # Placement failed. Report exactly what happened instead of claiming a
        # restoration that may not have happened. Three distinct states:
        #   A. a previous install existed and its automatic restore succeeded;
        #   B. a previous install existed but its automatic restore ALSO
        #      failed — the backup is kept (never deleted, never overwritten)
        #      and its exact path is printed so the user can restore manually;
        #   C. no previous install existed, so there was nothing to restore.
        if [ "$moved_old" = true ]; then
            # Test-only fault injection, off by default and never set in normal
            # use: occupy the destination with a plain file so the restore move
            # below genuinely fails (a directory cannot replace a file) while
            # the backup directory is left intact. Only reachable after the old
            # install is safely in backup.
            if [ "${OFFER_SELECTION_INSTALLER_TEST_FAIL_RESTORE:-0}" = "1" ]; then
                : > "$INSTALL_DIR" 2>/dev/null || true
            fi
            if mv "$old" "$INSTALL_DIR" 2>/dev/null; then
                error "Failed to place the new install at ${INSTALL_DIR}."
                error "The previous install was restored successfully."
                exit 3
            fi
            error "Failed to place the new install at ${INSTALL_DIR}."
            error "Automatic restoration also failed."
            error "The previous install is preserved at ${old}."
            error "To restore it manually, run:  mv '${old}' '${INSTALL_DIR}'"
            exit 3
        fi
        error "Failed to place the new install at ${INSTALL_DIR}."
        error "No previous installation existed to restore."
        exit 3
    fi
    STAGING_DIR=""
    if [ "$moved_old" = true ]; then
        rm -rf "$old" 2>/dev/null || true
    fi
    success "Installed ${SKILL_NAME} to ${INSTALL_DIR}"
}

install_files() {
    # Path + ownership checks run in dry-run too, so the preview is accurate
    # and an unsafe --path fails instead of being reported as installable.
    assert_safe_install_dir
    validate_existing_destination

    if $DRY_RUN; then
        printf "\n${BOLD}Dry-run mode — no files will be copied.${NC}\n\n"
        info "Would create directory: ${INSTALL_DIR}"
        info "Runtime allowlist (the complete install payload):"
        for entry in $(runtime_allowlist); do
            if [ ! -e "${SCRIPT_DIR}/${entry}" ]; then
                error "Would copy: ${entry}  (MISSING in the source package)"
                exit 1
            fi
            if [ -d "${SCRIPT_DIR}/${entry}" ]; then
                info "Would copy: ${entry}/  (directory)"
            else
                info "Would copy: ${entry}"
            fi
        done
        info "Would write ownership marker: ${MARKER_NAME} (schema ${MARKER_SCHEMA})"
        printf "\n"
        info "Never installed: ${FORBIDDEN_DIRS}"
        info "Installer scripts and developer docs (README/CONTRIBUTING/SECURITY/AGENTS) are never copied."
        return 0
    fi

    prepare_staging
    stage_runtime_files
    WORK_DIR="$STAGING_DIR"
    run_adapters
    generate_agents_md
    verify_staged_runtime
    commit_staged_install
}

# ---------------------------------------------------------------------------
# Run format adapters based on platform
# ---------------------------------------------------------------------------
run_adapters() {
    target="${WORK_DIR:-$INSTALL_DIR}"
    case "$PLATFORM" in
        # Cursor and Windsurf both discover native Agent Skills. Preserve the
        # complete SKILL.md package and progressive-disclosure semantics rather
        # than converting it into an always-present rule.
        cursor|windsurf)
            ;;
        cline)
            generate_plain_rule "$target" "${SKILL_NAME}.md"
            ;;
        roo-code)
            generate_plain_rule "$target" "${SKILL_NAME}.md"
            ;;
        kilo-code)
            generate_plain_rule "$target" "${SKILL_NAME}.md"
            ;;
        trae)
            generate_plain_rule "$target" "${SKILL_NAME}.md"
            ;;
        junie)
            generate_junie_guideline "$target"
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Activation instructions
# ---------------------------------------------------------------------------
print_activation_instructions() {
    if $DRY_RUN; then
        return 0
    fi

    printf "\n${GREEN}${BOLD}Installation complete!${NC}\n\n"

    case "$PLATFORM" in
        claude-code)
            printf "To activate the skill in Claude Code:\n"
            printf "  1. Start a new Claude Code session.\n"
            printf "  2. The skill will be loaded automatically from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke with /${SKILL_NAME} or use trigger phrases.\n"
            ;;
        workbuddy)
            printf "To activate the skill in WorkBuddy:\n"
            printf "  1. Restart WorkBuddy or reload Skills.\n"
            printf "  2. The native skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Ask it to compare postgraduate offers or select the skill in WorkBuddy.\n"
            ;;
        github-copilot)
            printf "To activate the skill in GitHub Copilot:\n"
            printf "  1. Open your project in VS Code or the GitHub CLI.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke with /${SKILL_NAME} or reference in instructions.\n"
            ;;
        cursor)
            printf "To activate the skill in Cursor:\n"
            printf "  1. Open your project in Cursor.\n"
            printf "  2. Cursor discovers the native skill at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke /${SKILL_NAME} or use a matching request.\n"
            ;;
        windsurf)
            printf "To activate the skill in Windsurf:\n"
            printf "  1. Open your project in Windsurf.\n"
            printf "  2. Windsurf discovers the native skill at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke @${SKILL_NAME} or use a matching request.\n"
            ;;
        cline)
            printf "To activate the skill in Cline:\n"
            printf "  1. Open your project in VS Code with Cline.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Cline will pick up the rule automatically.\n"
            ;;
        codex)
            printf "To activate the skill in OpenAI Codex CLI:\n"
            printf "  1. Start a new Codex CLI session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke with /skills or \$${SKILL_NAME}.\n"
            ;;
        gemini)
            printf "To activate the skill in Gemini CLI:\n"
            printf "  1. Start a new Gemini CLI session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. The skill will be loaded automatically.\n"
            ;;
        kiro)
            printf "To activate the skill in Kiro:\n"
            printf "  1. Open your project in Kiro.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke with / or use trigger phrases.\n"
            ;;
        trae)
            printf "To activate the skill in Trae:\n"
            printf "  1. Open your project in Trae.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Use trigger phrases or Intelligent mode.\n"
            ;;
        goose)
            printf "To activate the skill in Goose:\n"
            printf "  1. Start a new Goose session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Say 'Use the ${SKILL_NAME} skill' or use trigger phrases.\n"
            ;;
        opencode)
            printf "To activate the skill in OpenCode:\n"
            printf "  1. Start a new OpenCode session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. OpenCode reads from ~/.config/opencode/skills/ automatically.\n"
            ;;
        roo-code)
            printf "To activate the skill in Roo Code:\n"
            printf "  1. Open your project in VS Code with Roo Code.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Use /orchestrator, /code, or trigger phrases.\n"
            ;;
        kilo-code)
            printf "To activate the skill in Kilo Code:\n"
            printf "  1. Open your project in VS Code/JetBrains with Kilo Code.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Kilo Code will pick up the rule automatically.\n"
            ;;
        factory)
            printf "To activate the skill in Factory Droid:\n"
            printf "  1. Start a new Factory Droid session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Invoke with /${SKILL_NAME} or /droids menu.\n"
            ;;
        junie)
            printf "To activate the skill in Junie:\n"
            printf "  1. Open your project in JetBrains with Junie.\n"
            printf "  2. The guideline is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/guidelines.md${NC}\n"
            printf "  3. Junie loads guidelines automatically.\n"
            ;;
        antigravity)
            printf "To activate the skill in Antigravity:\n"
            printf "  1. Open your project.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Antigravity reads from .agent/skills/ automatically.\n"
            printf "  Note: .agent/ (singular), NOT .agents/ (plural).\n"
            ;;
        universal)
            printf "The skill is installed at the universal path:\n"
            printf "  ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n\n"
            printf "Tools that read ~/.agents/skills/ (Codex CLI, Gemini CLI,\n"
            printf "OpenCode, Goose, Cline, Roo Code, Kilo Code) will discover it.\n"
            ;;
    esac

    printf "\n"
}

# ---------------------------------------------------------------------------
# Install for a single platform
# ---------------------------------------------------------------------------
install_single() {
    detect_platform
    resolve_install_path
    if $DRY_RUN; then
        WORK_DIR="$INSTALL_DIR"
    fi
    install_files
    if $DRY_RUN; then
        # Adapters only report; nothing is staged in dry-run mode.
        run_adapters
        generate_agents_md
    fi
    install_universal_secondary
    print_activation_instructions

    if $DRY_RUN; then
        info "Dry run complete. No changes were made."
    else
        success "Skill '${SKILL_NAME}' installed successfully for ${PLATFORM}."
    fi
}

# ---------------------------------------------------------------------------
# Install for all detected platforms (--all)
# ---------------------------------------------------------------------------
install_all() {
    if [ -n "$CUSTOM_PATH" ]; then
        error "--path cannot be combined with --all"
        exit 1
    fi
    detect_all_platforms
    info "Installing to all detected platforms: ${ALL_PLATFORMS}"
    printf "%-40s\n" "----------------------------------------"

    installed_count=0
    first_non_agents_dir=""
    for plat in $ALL_PLATFORMS; do
        printf "\n"
        info "--- Installing for: ${plat} ---"
        PLATFORM="$plat"
        resolve_install_path
        install_files
        if $DRY_RUN; then
            WORK_DIR="$INSTALL_DIR"
            run_adapters
            generate_agents_md
        fi
        installed_count=$((installed_count + 1))
        # Remember the first non-.agents/ install dir for universal symlink
        if [ -z "$first_non_agents_dir" ]; then
            case "$plat" in
                codex|universal) ;;
                *) first_non_agents_dir="$INSTALL_DIR" ;;
            esac
        fi
    done

    # Create universal symlink from the first non-.agents/ install
    if [ -n "$first_non_agents_dir" ]; then
        INSTALL_DIR="$first_non_agents_dir"
        install_universal_secondary
    fi

    printf "\n"
    if $DRY_RUN; then
        info "Dry run complete. No changes were made."
    else
        success "Skill '${SKILL_NAME}' installed to ${installed_count} platform(s)."
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    trap cleanup EXIT HUP INT TERM

    detect_version
    parse_args "$@"

    printf "${BOLD}Installing skill: ${SKILL_NAME} (v${VERSION})${NC}\n"
    printf "%-40s\n" "----------------------------------------"

    validate_skill_md

    if $INSTALL_ALL; then
        install_all
    else
        install_single
    fi

    exit 0
}

main "$@"
