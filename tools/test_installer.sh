#!/usr/bin/env bash
# test_installer.sh — read-only installer safety battery (dev tool, not shipped)
#
# Exercises install.sh against temp directories: legal fresh installs, paths
# with spaces, basename rejection, refusal of / $HOME / the source package and
# its ancestors, refusal to overwrite unmanaged directories (sentinel file
# preserved), managed marker upgrades, symlink refusal, invalid-marker
# refusal, unmarked-copy protection, exact payload matching and runtime-reference
# completeness. Exits non-zero if any assertion fails.
#
# Usage:  bash tools/test_installer.sh
# CI:     .github/workflows/ci.yml runs this after `bash -n`.

set -u

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$REPO_DIR/skills/offer-selection-skill"
cd "$REPO_DIR" || { echo "cannot cd to $REPO_DIR"; exit 1; }

PASS=0
FAIL=0
ok()  { PASS=$((PASS + 1)); echo "PASS: $1"; }
bad() { FAIL=$((FAIL + 1)); echo "FAIL: $1"; }

T="$(mktemp -d "${TMPDIR:-/tmp}/oss-installer-test.XXXXXX")"
trap 'rm -rf "$T"' EXIT

# 1. Fresh install to a legal (nonexistent) path succeeds.
if ./install.sh --platform universal --path "$T/1/offer-selection-skill" >/dev/null 2>&1 &&
   [ -f "$T/1/offer-selection-skill/SKILL.md" ] &&
   [ -f "$T/1/offer-selection-skill/.offer-selection-skill-install.json" ]; then
  ok "1. fresh legal path"
else
  bad "1. fresh legal path"
fi

# 2. A parent directory containing spaces still works when the basename is the
#    skill name.
if ./install.sh --platform universal --path "$T/my skills dir/offer-selection-skill" >/dev/null 2>&1 &&
   [ -f "$T/my skills dir/offer-selection-skill/SKILL.md" ]; then
  ok "2. parent path with spaces"
else
  bad "2. parent path with spaces"
fi

# 3. A basename that is not the skill name is rejected (not warned).
if ./install.sh --platform universal --path "$T/3/not-the-skill" >/dev/null 2>&1; then
  bad "3. basename rejection"
else
  ok "3. basename rejection"
fi

# 4. /, $HOME, the source package and an ancestor of the source are rejected.
if ./install.sh --platform universal --path "/" >/dev/null 2>&1; then
  bad "4. '/' rejection"
else
  ok "4. '/' rejection"
fi
if ./install.sh --platform universal --path "$HOME" >/dev/null 2>&1; then
  bad "4. \$HOME rejection"
else
  ok "4. \$HOME rejection"
fi
if ./install.sh --platform universal --path "$REPO_DIR" >/dev/null 2>&1; then
  bad "4. source-package rejection"
else
  ok "4. source-package rejection"
fi
if ./install.sh --platform universal --path "$(dirname "$REPO_DIR")" >/dev/null 2>&1; then
  bad "4. source-ancestor rejection"
else
  ok "4. source-ancestor rejection"
fi

# 5. An existing directory with no marker and no legacy skill layout is refused
#    and its contents are preserved.
mkdir -p "$T/5/offer-selection-skill"
echo sentinel > "$T/5/offer-selection-skill/precious.txt"
if ./install.sh --platform universal --path "$T/5/offer-selection-skill" >/dev/null 2>&1; then
  bad "5. stranger-directory refusal"
else
  ok "5. stranger-directory refusal"
fi
if [ "$(cat "$T/5/offer-selection-skill/precious.txt")" = "sentinel" ]; then
  ok "5. sentinel preserved"
else
  bad "5. sentinel preserved"
fi

# 6. An existing install carrying a valid ownership marker can be upgraded.
if ./install.sh --platform universal --path "$T/6/offer-selection-skill" >/dev/null 2>&1 &&
   ./install.sh --platform universal --path "$T/6/offer-selection-skill" >/dev/null 2>&1 &&
   [ -f "$T/6/offer-selection-skill/.offer-selection-skill-install.json" ]; then
  ok "6. managed marker upgrade"
else
  bad "6. managed marker upgrade"
fi

# 7. A symlink whose basename IS the skill name is refused by the link
#    protection (the basename check alone cannot explain the refusal) and the
#    symlink target is untouched.
mkdir -p "$T/7" "$T/7real"
echo data > "$T/7real/data.txt"
ln -s "$T/7real" "$T/7/offer-selection-skill"
if ./install.sh --platform universal --path "$T/7/offer-selection-skill" >/dev/null 2>&1; then
  bad "7. link destination refused by link protection"
else
  ok "7. link destination refused by link protection"
fi
if [ "$(cat "$T/7real/data.txt")" = "data" ] &&
   [ ! -e "$T/7real/SKILL.md" ] &&
   [ ! -e "$T/7real/.offer-selection-skill-install.json" ]; then
  ok "7. link target untouched (sentinel intact, no SKILL.md/marker added)"
else
  bad "7. link target untouched (sentinel intact, no SKILL.md/marker added)"
fi
if [ -L "$T/7/offer-selection-skill" ]; then
  ok "7. link still present after refusal"
else
  bad "7. link still present after refusal"
fi

# 8. A marker whose name/schema does not match is refused and preserved.
mkdir -p "$T/8/offer-selection-skill"
printf '{"schema":"offer-selection-skill-install/v1","name":"other-skill","version":"9"}\n' \
  > "$T/8/offer-selection-skill/.offer-selection-skill-install.json"
if ./install.sh --platform universal --path "$T/8/offer-selection-skill" >/dev/null 2>&1; then
  bad "8. invalid-marker refusal"
else
  ok "8. invalid-marker refusal"
fi
if [ -f "$T/8/offer-selection-skill/.offer-selection-skill-install.json" ]; then
  ok "8. invalid marker preserved"
else
  bad "8. invalid marker preserved"
fi

# 9. A complete skill layout is not proof of installer ownership.
mkdir -p "$T/9/offer-selection-skill/references" \
         "$T/9/offer-selection-skill/.claude-plugin"
cp "$SKILL_DIR/SKILL.md" "$T/9/offer-selection-skill/SKILL.md"
cp "$SKILL_DIR"/references/*.md "$T/9/offer-selection-skill/references/"
if ./install.sh --platform universal --path "$T/9/offer-selection-skill" >/dev/null 2>&1; then
  bad "9. unmarked complete skill must be refused"
elif [ ! -e "$T/9/offer-selection-skill/.offer-selection-skill-install.json" ] &&
     cmp -s "$SKILL_DIR/SKILL.md" "$T/9/offer-selection-skill/SKILL.md"; then
  ok "9. unmarked complete skill refused and preserved"
else
  bad "9. unmarked skill changed"
fi

# 10. Exact payload: top-level entries equal the allowlist plus the marker, and
#     dev material is absent.
INSTALL="$T/1/offer-selection-skill"
ACTUAL="$(ls -A "$INSTALL" | sort)"
EXPECTED="$(printf '%s\n' .claude-plugin .offer-selection-skill-install.json LICENSE SKILL.md references | sort)"
if [ "$ACTUAL" = "$EXPECTED" ]; then
  ok "10. payload exact match"
else
  bad "10. payload exact match (got: $ACTUAL)"
fi
FORBIDDEN_PRESENT=""
for d in README.md CONTRIBUTING.md SECURITY.md AGENTS.md audits evals archive tools \
         .git .workbuddy .DS_Store __pycache__ install.sh install.ps1; do
  if [ -e "$INSTALL/$d" ]; then FORBIDDEN_PRESENT="$FORBIDDEN_PRESENT $d"; fi
done
if [ -z "$FORBIDDEN_PRESENT" ]; then
  ok "10. no dev docs / dev material / installer scripts installed"
else
  bad "10. forbidden entries present:$FORBIDDEN_PRESENT"
fi

# 11. Every runtime reference resolves from the installed copy, and the marker
#     JSON parses with the correct schema/name/version.
MISSING=""
for f in SKILL.md references/core-decision-engine.md references/path-private-sector.md \
         references/path-soe-public.md references/path-local-stay.md \
         references/path-phd-academic.md references/priors-and-calibration.md; do
  [ -f "$INSTALL/$f" ] || MISSING="$MISSING $f"
done
if [ -z "$MISSING" ]; then
  ok "11. runtime references complete"
else
  bad "11. missing runtime files:$MISSING"
fi
PLUGIN_VER="$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")"
if python3 - "$INSTALL/.offer-selection-skill-install.json" "$PLUGIN_VER" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
assert d.get("schema") == "offer-selection-skill-install/v1", d
assert d.get("name") == "offer-selection-skill", d
assert d.get("version") == sys.argv[2], (d.get("version"), sys.argv[2])
PY
then
  ok "11. marker JSON valid (schema/name/version)"
else
  bad "11. marker JSON invalid"
fi

# 12. Real rollback fault injection: a marker-managed upgrade fails AFTER the
#     old install has moved to backup (test-only hook), so the real placement
#     failure path must restore the previous install and leave no
#     .previous.*/staging residue.
RB="$T/12/offer-selection-skill"
if ! ./install.sh --platform universal --path "$RB" >/dev/null 2>&1; then
  bad "12. rollback setup (initial managed install failed)"
else
  echo rollback-sentinel > "$RB/sentinel.txt"
fi
if OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP=1 \
     ./install.sh --platform universal --path "$RB" >/dev/null 2>&1; then
  bad "12. rollback: upgrade unexpectedly succeeded"
else
  ok "12. rollback: upgrade failed under injected placement failure"
fi
if [ -f "$RB/SKILL.md" ] && [ -f "$RB/.offer-selection-skill-install.json" ]; then
  ok "12. rollback: previous install restored (SKILL.md + marker)"
else
  bad "12. rollback: previous install not restored"
fi
if [ "$(cat "$RB/sentinel.txt")" = "rollback-sentinel" ]; then
  ok "12. rollback: sentinel content unchanged"
else
  bad "12. rollback: sentinel content changed"
fi
LEFT="$(ls -A "$T/12")"
if [ "$LEFT" = "offer-selection-skill" ]; then
  ok "12. rollback: no .previous.* or staging leftover"
else
  bad "12. rollback: leftover entries: $LEFT"
fi

# 13. Restore-failure fault injection: when BOTH placement and the automatic
#     restore fail (test-only hooks), the installer must keep the backup
#     (never delete or overwrite it), print its exact path, and must NOT claim
#     that it restored the previous install.
RB="$T/13/offer-selection-skill"
if ! ./install.sh --platform universal --path "$RB" >/dev/null 2>&1; then
  bad "13. restore-failure setup (initial managed install failed)"
else
  echo restore-fail-sentinel > "$RB/sentinel.txt"
fi
OUT="$T/13.out"
if OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP=1 \
   OFFER_SELECTION_INSTALLER_TEST_FAIL_RESTORE=1 \
   ./install.sh --platform universal --path "$RB" >"$OUT" 2>&1; then
  bad "13. restore-failure: upgrade unexpectedly succeeded"
else
  ok "13. restore-failure: upgrade failed (placement + restore both injected to fail)"
fi
if grep -q "Automatic restoration also failed" "$OUT"; then
  ok "13. restore-failure: output reports the automatic restoration failure"
else
  bad "13. restore-failure: output does not report the automatic restoration failure"
fi
if grep -q "restored successfully" "$OUT"; then
  bad "13. restore-failure: output falsely claims a successful restore"
else
  ok "13. restore-failure: output does not falsely claim a restore"
fi
BACKUP=""
for d in "$T/13"/.offer-selection-skill.previous.*; do
  [ -d "$d" ] && BACKUP="$d"
done
if [ -n "$BACKUP" ]; then
  ok "13. restore-failure: previous install preserved in a backup directory"
else
  bad "13. restore-failure: no backup directory found"
fi
if [ -n "$BACKUP" ]; then
  if grep -qF "$BACKUP" "$OUT"; then
    ok "13. restore-failure: output reports the backup path"
  else
    bad "13. restore-failure: output does not report the backup path"
  fi
  if [ -f "$BACKUP/SKILL.md" ] && \
     [ -f "$BACKUP/.offer-selection-skill-install.json" ] && \
     [ "$(cat "$BACKUP/sentinel.txt")" = "restore-fail-sentinel" ]; then
    ok "13. restore-failure: backup intact (SKILL.md + marker + sentinel)"
  else
    bad "13. restore-failure: backup incomplete or sentinel changed"
  fi
fi
if [ ! -d "$RB" ] && [ ! -e "$RB/SKILL.md" ] && \
   [ ! -e "$RB/.offer-selection-skill-install.json" ]; then
  ok "13. restore-failure: destination not occupied by a new install"
else
  bad "13. restore-failure: destination wrongly occupied by a new install"
fi
if [ -z "$(ls -A "$T/13" 2>/dev/null | grep '\.staging\.' || true)" ]; then
  ok "13. restore-failure: no staging leftover"
else
  bad "13. restore-failure: staging leftover present"
fi

# 14. Cursor and Windsurf use their native Agent Skills directories. The
# complete package must be installed without generated rule files.
mkdir -p "$T/14-cursor" "$T/14-windsurf"
if (cd "$T/14-cursor" && "$REPO_DIR/install.sh" --platform cursor --project >/dev/null 2>&1) &&
   [ -f "$T/14-cursor/.cursor/skills/offer-selection-skill/SKILL.md" ] &&
   [ ! -e "$T/14-cursor/.cursor/skills/offer-selection-skill/offer-selection-skill.mdc" ]; then
  ok "14. Cursor native skill layout (no rule adapter)"
else
  bad "14. Cursor native skill layout (no rule adapter)"
fi
if (cd "$T/14-windsurf" && "$REPO_DIR/install.sh" --platform windsurf --project >/dev/null 2>&1) &&
   [ -f "$T/14-windsurf/.windsurf/skills/offer-selection-skill/SKILL.md" ] &&
   [ ! -e "$T/14-windsurf/.windsurf/skills/offer-selection-skill/offer-selection-skill.md" ]; then
  ok "14. Windsurf native skill layout (no rule adapter)"
else
  bad "14. Windsurf native skill layout (no rule adapter)"
fi

# 15. A repository's ordinary .github directory is not proof that Copilot is
# installed. Auto-detection must fail instead of silently selecting it.
mkdir -p "$T/15/project/.github" "$T/15/home"
if (cd "$T/15/project" && HOME="$T/15/home" "$REPO_DIR/install.sh" --dry-run >/dev/null 2>&1); then
  bad "15. .github does not auto-detect Copilot"
else
  ok "15. .github does not auto-detect Copilot"
fi

# 16. WorkBuddy receives the complete native skill package in its documented
# user-level skills directory.
mkdir -p "$T/16/home/.workbuddy/skills"
if HOME="$T/16/home" ./install.sh --platform workbuddy >/dev/null 2>&1 &&
   [ -f "$T/16/home/.workbuddy/skills/offer-selection-skill/SKILL.md" ] &&
   [ -f "$T/16/home/.workbuddy/skills/offer-selection-skill/references/core-decision-engine.md" ]; then
  ok "16. WorkBuddy native skill layout"
else
  bad "16. WorkBuddy native skill layout"
fi

# 17. The three first-class hosts can coexist. A secondary convenience link
# may be migrated to a standalone Codex install, while the WorkBuddy and Claude
# copies remain intact.
mkdir -p "$T/17/home/.workbuddy/skills" "$T/17/home/.claude/skills"
if HOME="$T/17/home" ./install.sh --platform workbuddy >/dev/null 2>&1 &&
   HOME="$T/17/home" ./install.sh --platform claude-code >/dev/null 2>&1 &&
   HOME="$T/17/home" ./install.sh --platform codex >/dev/null 2>&1 &&
   [ -f "$T/17/home/.workbuddy/skills/offer-selection-skill/SKILL.md" ] &&
   [ -f "$T/17/home/.claude/skills/offer-selection-skill/SKILL.md" ] &&
   [ -f "$T/17/home/.agents/skills/offer-selection-skill/SKILL.md" ] &&
   [ ! -L "$T/17/home/.agents/skills/offer-selection-skill" ]; then
  ok "17. Codex + WorkBuddy + Claude Code coexist"
else
  bad "17. Codex + WorkBuddy + Claude Code coexist"
fi

echo "----"
echo "installer battery: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
