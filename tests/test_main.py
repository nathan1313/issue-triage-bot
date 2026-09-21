"""Hello-world smoke test for v0.1.

The point of this PR isn't to ship a feature — it's to prove
the bot runs inside an Action context. So tests cover:

- _build_comment produces a non-empty string referencing the
  issue title
- main() with --input + --dry-run prints without contacting GitHub
- main() with no args and no GITHUB_EVENT_PATH exits with a
  helpful error

PR B will add real Jev tests against mocked HTTP responses.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"


def _setup_path():
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))


class TestBuildComment(unittest.TestCase):

    def setUp(self):
        _setup_path()
        from triage_bot import __main__ as tb
        self.tb = tb

    def test_comment_contains_title(self):
        issue = {"title": "Login button doesn't work"}
        body = self.tb._build_comment(issue)
        self.assertIn("Login button doesn't work", body)
        self.assertIn("issue-triage-bot", body)

    def test_comment_handles_missing_title(self):
        body = self.tb._build_comment({})
        self.assertIn("(no title)", body)


class TestDryRun(unittest.TestCase):

    def setUp(self):
        _setup_path()
        from triage_bot import __main__ as tb
        self.tb = tb

    def test_dry_run_prints_without_posting(self):
        payload = {"issue": {"number": 42, "title": "Test issue"}}
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False) as f:
            json.dump(payload, f)
            path = f.name
        try:
            # Make sure no GITHUB_EVENT_PATH so we hit the CLI path.
            env = os.environ.copy()
            env.pop("GITHUB_EVENT_PATH", None)
            proc = subprocess.run(
                [sys.executable, "-m", "triage_bot",
                 "--input", path, "--dry-run"],
                capture_output=True, text=True,
                cwd=str(REPO_ROOT), env=env, timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("DRY RUN", proc.stdout)
            self.assertIn("Test issue", proc.stdout)
        finally:
            os.unlink(path)

    def test_main_without_input_errors(self):
        env = os.environ.copy()
        env.pop("GITHUB_EVENT_PATH", None)
        proc = subprocess.run(
            [sys.executable, "-m", "triage_bot"],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT), env=env, timeout=10,
        )
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
