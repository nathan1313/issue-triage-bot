"""Smoke tests for the triage bot bootstrap (issue #2).

Uses stdlib unittest only so the workflow stays hermetic (no pytest
dependency at bootstrap time).
"""

import json
import os
import sys
import unittest

# Make .github/triage.py importable without installing anything.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, ".github"))

from triage import handle_issue  # noqa: E402

_FIXTURE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fixtures",
    "triage",
    "issue_opened.json",
)


class HandleIssueSmokeTest(unittest.TestCase):
    def setUp(self):
        with open(_FIXTURE_PATH, encoding="utf-8") as fh:
            self.payload = json.load(fh)

    def test_handle_issue_without_api_key(self):
        result = handle_issue(self.payload, None)
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "no_api_key")

    def test_handle_issue_with_api_key(self):
        # Downstream tickets (#1, label-apply, comment-post) have not
        # landed yet, so a key present still short-circuits to pending
        # rather than raising NotImplementedError from the stubs.
        result = handle_issue(self.payload, "fake-key")
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["reason"], "downstream_not_implemented")


if __name__ == "__main__":
    unittest.main()
