"""Release-contract checks: version parity, shipped-file privacy, stdlib-only engine."""

import ast
import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ("skills", "maintenance", "docs", ".claude-plugin", "README.md", "CHANGELOG.md")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".zip"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
LOCAL_PATH = re.compile(r"(?:/Users/|[A-Za-z]:\\\\Users\\\\)[A-Za-z0-9._-]+")


def shipped_files():
    try:
        listed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True,
                                text=True, check=True).stdout.split("\0")
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

    def test_release_status_stays_candidate(self):
        status = (ROOT / "docs/RELEASE_STATUS.md").read_text()
        self.assertIn("候选", status)
        for claim in ("Stable 已发布", "已正式发布", "production stable"):
            self.assertNotIn(claim, status)

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


if __name__ == "__main__":
    unittest.main()
