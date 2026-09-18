#!/usr/bin/env python3
"""Frontmatter compliance check for SKILL.md (local equivalent of the official
Agent Skills `skills-ref` validator).

Dev tool. Python standard library only (no PyYAML dependency). Run from the
repository root:

    python3 tools/check_frontmatter.py

The frontmatter is a small, controlled YAML subset: top-level scalar keys, one
folded `description` block, and one nested `metadata` mapping whose values are
all strings. The standard library has no YAML parser, so this checker parses
exactly that subset and FAILS CLOSED on anything outside it — it is not and
does not try to be a general YAML parser.

Checks (Agent Skills specification surface):
  1. only official top-level keys are present
     (name description license compatibility metadata allowed-tools)
  2. `name` matches the directory name and ^[a-z0-9]+(-[a-z0-9]+)*$
  3. `description` is non-empty and at most 1024 characters
  4. `metadata` is a mapping whose keys and values are all strings
     (any value YAML would read as a non-string type is rejected)
  5. `metadata.version` equals .claude-plugin/plugin.json version
  6. there is no top-level `activation` or `provenance` key

Exit code 0 = PASS, 1 = FAIL. The official `skills-ref` validator is a
separate, network-installable tool; this checker is its local equivalent and
its result must not be reported as an official `skills-ref` run.
"""

import json
import os
import re
import sys

ALLOWED_TOP_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# YAML implicit types that would make an unquoted metadata value a non-string.
NON_STRING_RE = re.compile(
    r"^(?:"
    r"[-+]?[0-9]+"                       # integer
    r"|[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?"  # float
    r"|true|false|True|False|TRUE|FALSE" # boolean
    r"|null|Null|NULL|~"                 # null
    r"|[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}"   # date
    r")$"
)


class CheckError(Exception):
    pass


def die(msg):
    raise CheckError(msg)


def parse_frontmatter(text):
    """Parse the controlled frontmatter subset into (top, metadata)."""
    if not text.startswith("---\n"):
        die("frontmatter must open the file with '---'")
    body = text.split("\n---", 1)
    if len(body) < 2:
        die("frontmatter closing '---' not found")
    fm_lines = body[0].split("\n")[1:]  # drop the opening '---'

    top = {}
    metadata = {}
    meta_open = False
    folded_key = None
    folded_lines = []
    line_re = re.compile(r"^([A-Za-z0-9_.-]+):(.*)$")

    def close_folded():
        nonlocal folded_key
        if folded_key is not None:
            top[folded_key] = " ".join(folded_lines).strip()
            folded_key = None
            folded_lines.clear()

    for raw in fm_lines:
        line = raw.rstrip("\r\n")
        if line.strip() == "":
            if folded_key is not None:
                folded_lines.append("")
            continue
        if "\t" in line:
            die("tab indentation is not supported in the controlled frontmatter")
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            close_folded()
            m = line_re.match(line)
            if not m:
                die("unsupported top-level frontmatter line: %r" % line)
            key, rest = m.group(1), m.group(2).strip()
            meta_open = False
            if rest == "":
                top[key] = None  # nested mapping follows on indented lines
                if key == "metadata":
                    meta_open = True
            elif rest == ">-":
                top[key] = ""
                folded_key = key
            else:
                top[key] = rest
        else:
            if folded_key is not None:
                folded_lines.append(line.strip())
                continue
            m = line_re.match(line.strip())
            if not m:
                if line.strip().startswith("- "):
                    die("list values are not supported in the controlled frontmatter")
                die("unsupported indented frontmatter line: %r" % line)
            key, rest = m.group(1), m.group(2).strip()
            if not meta_open:
                die("indented key %r outside a supported nested mapping" % key)
            if rest == "":
                die("metadata key %r has no value (null is not a string)" % key)
            metadata[key] = rest
    close_folded()
    return top, metadata


def check():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_root = os.path.join(root, "skills", "offer-selection-skill")
    skill_md = os.path.join(skill_root, "SKILL.md")
    plugin_json = os.path.join(root, ".claude-plugin", "plugin.json")
    if not os.path.isfile(skill_md):
        die("SKILL.md not found at %s" % skill_md)
    if not os.path.isfile(plugin_json):
        die("plugin.json not found at %s" % plugin_json)

    with open(skill_md, encoding="utf-8") as fh:
        text = fh.read()
    top, metadata = parse_frontmatter(text)

    # 1 + 6: only official top-level keys; no activation/provenance.
    bad_keys = sorted(set(top) - ALLOWED_TOP_KEYS)
    if bad_keys:
        die("top-level key(s) not allowed by the Agent Skills spec: %s"
            % ", ".join(bad_keys))

    # 2: name present, format-valid, equals the skill directory name.
    name = top.get("name")
    if not name:
        die("top-level `name` is missing")
    if not NAME_RE.match(name):
        die("top-level `name` %r is not a valid skill name" % name)
    dir_name = os.path.basename(skill_root)
    if name != dir_name:
        die("top-level `name` %r does not match the skill directory name %r"
            % (name, dir_name))

    # 3: description non-empty and <= 1024 chars.
    description = top.get("description", "")
    if not description or not description.strip():
        die("top-level `description` is empty")
    if len(description) > 1024:
        die("top-level `description` is %d chars (limit 1024)" % len(description))

    # 4: metadata is a mapping of string keys and string values.
    if "metadata" not in top:
        die("top-level `metadata` is missing")
    if not metadata:
        die("`metadata` is not a mapping (or is empty)")
    for key, value in metadata.items():
        if NON_STRING_RE.match(value):
            die("metadata.%s value %r would parse as a non-string in YAML; "
                "quote it" % (key, value))

    # 5: metadata.version == plugin.json version.
    version = metadata.get("version")
    if not version:
        die("metadata.version is missing")
    version = version.strip("\"'")
    with open(plugin_json, encoding="utf-8") as fh:
        plugin = json.load(fh)
    plugin_version = plugin.get("version")
    if plugin_version != version:
        die("version mismatch: metadata.version=%s plugin.json=%s"
            % (version, plugin_version))

    print("frontmatter compliance: PASS (name=%s, version=%s, metadata keys=%d, description=%d chars)"
          % (name, version, len(metadata), len(description)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(check())
    except CheckError as exc:
        print("frontmatter compliance: FAIL — %s" % exc, file=sys.stderr)
        sys.exit(1)
