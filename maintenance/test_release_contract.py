"""Release-contract checks: version parity, shipped-file privacy, stdlib-only engine."""

import ast
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ("skills", "maintenance", "docs", ".claude-plugin", "README.md", "LICENSE", "SECURITY.md")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".zip"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
LOCAL_PATH = re.compile(r"(?:/Users/|[A-Za-z]:\\\\Users\\\\)[A-Za-z0-9._-]+")
STABLE_CLAIMS = ("Stable 已发布", "已正式发布", "production stable", "正式版**")


def status_doc_errors(status, docs):
    if status not in {"candidate", "stable"}:
        return ["release_status must be candidate or stable"]
    if status == "candidate":
        errors = [] if "候选版" in docs else ["candidate docs must contain 候选版"]
        errors += [f"candidate docs must not contain {claim}"
                   for claim in STABLE_CLAIMS if claim in docs]
        return errors
    errors = [] if "正式版" in docs else ["stable docs must contain 正式版"]
    if "候选版" in docs:
        errors.append("stable docs must not contain 候选版")
    return errors


def shipped_files():
    try:
        listed = subprocess.run(["git", "ls-files", "-z", "--", *SHIPPED], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.split("\0")
        paths = [ROOT / p for p in listed if p]
    except (OSError, subprocess.CalledProcessError):
        paths = [p for name in SHIPPED for p in (ROOT / name).rglob("*")]
        paths = [p for p in paths if p.is_file()]
    return [p for p in paths if p.is_file() and p.suffix.lower() not in SKIP_SUFFIXES]


class ReleaseContract(unittest.TestCase):
    def test_version_is_single_sourced(self):
        version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"]
        skill = (ROOT / "skills/offer-selection-skill/SKILL.md").read_text()
        self.assertIn(f'version: "{version}"', skill)
        self.assertIn(f'FALLBACK_VERSION="{version}"', (ROOT / "maintenance/install.sh").read_text())
        self.assertIn(f'$FallbackVersion = "{version}"', (ROOT / "maintenance/install.ps1").read_text())

    def test_release_status_matches_docs(self):
        manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        docs = (ROOT / "docs/RELEASE_STATUS.md").read_text()
        self.assertEqual(status_doc_errors(manifest.get("release_status"), docs), [])

    def test_stable_status_switch_contract(self):
        self.assertEqual(status_doc_errors("stable", "本分支为 **v1.0.0 正式版**。"), [])
        self.assertNotEqual(status_doc_errors("stable", "本分支为 **v1.0.0 候选版**。"), [])
        self.assertNotEqual(status_doc_errors("candidate", "本分支为 **v1.0.0 正式版**。"), [])
        self.assertNotEqual(status_doc_errors("preview", "候选版"), [])

    def test_installer_ships_only_runtime_files(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "offer-selection-skill"
            subprocess.run([str(ROOT / "maintenance/install.sh"), "--path", str(dest)],
                           check=True, capture_output=True, text=True)
            files = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
            forbidden = {"internal", "evals", "audits", "archive", "tools"}
            self.assertFalse({f for f in files if f.split("/")[0] in forbidden},
                             "development material leaked into the runtime install")
            self.assertIn("scripts/decision.py", files)
            self.assertIn("scripts/harness.py", files)
            self.assertIn("references/core-decision-engine.md", files)
            self.assertNotIn("docs/RELEASE_STATUS.md", files)

    def test_custom_path_install_needs_no_host_client(self):
        # A clean machine/CI runner has no ~/.claude, ~/.cursor, ... directories.
        # --path is an explicit destination and must not depend on detection.
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "clean-home"
            home.mkdir()
            dest = Path(temp) / "root" / "offer-selection-skill"
            env = {**os.environ, "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config")}
            result = subprocess.run([str(ROOT / "maintenance/install.sh"), "--path", str(dest)],
                                    capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest / "SKILL.md").is_file())

    def test_local_stay_covers_post_initial_visa_path(self):
        rule = (ROOT / "skills/offer-selection-skill/references/path-local-stay.md").read_text()
        for required in ("IANG", "extension/renewal", "unresolved or conditional",
                         "initial grant"):
            self.assertIn(required, rule)

    def test_no_machine_local_paths_in_shipped_files(self):
        hits = [f"{p.relative_to(ROOT)}: {m.group(0)}"
                for p in shipped_files() for m in LOCAL_PATH.finditer(p.read_text(errors="ignore"))]
        self.assertEqual(hits, [], "absolute local paths in shipped files")

    def test_no_credentials_or_private_keys(self):
        hits = []
        for path in shipped_files():
            text = path.read_text(errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    hits.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")
        self.assertEqual(hits, [], "credential-like material in shipped files")

    def test_engine_imports_stdlib_only(self):
        tree = ast.parse((ROOT / "skills/offer-selection-skill/scripts/decision.py").read_text())
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                modules.add(node.module.split(".")[0])
        self.assertEqual(modules, {"argparse", "json", "re", "sys", "copy", "datetime",
                                   "pathlib", "urllib"})

    def test_harness_imports_stdlib_and_the_engine_only(self):
        tree = ast.parse((ROOT / "skills/offer-selection-skill/scripts/harness.py").read_text())
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                modules.add(node.module.split(".")[0])
        self.assertEqual(modules, {"argparse", "copy", "datetime", "hashlib", "json",
                                   "os", "re", "sys", "pathlib", "decision"})


if __name__ == "__main__":
    unittest.main()
