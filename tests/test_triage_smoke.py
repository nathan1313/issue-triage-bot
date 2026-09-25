"""Smoke tests for the triage bootstrap (ticket #2).

Uses stdlib ``unittest`` to keep the workflow hermetic — no pytest
dependency until a later ticket introduces it.
"""

import json
import os
import sys
import unittest

# Make the bootstrap module importable. ``.github/triage.py`` lives outside
# the ``tests/`` tree, so we extend ``sys.path`` explicitly.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, ".github"))

import triage  # noqa: E402


FIXTURE_PATH = os.path.join(
    ROOT, "tests", "fixtures", "triage", "issue_opened.json"
)


class HandleIssueSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(FIXTURE_PATH, "r", encoding="utf-8") as fh:
            self.payload = json.load(fh)

    def test_handle_issue_without_api_key(self) -> None:
        result = triage.handle_issue(self.payload, None)
        self.assertEqual(
            result,
            {"status": "skipped", "reason": "no_api_key"},
        )

    def test_handle_issue_with_api_key_short_circuits(self) -> None:
        # ``classify`` / ``format_response`` are still stubs, so the
        # handler must short-circuit to ``pending`` rather than
        # propagating ``NotImplementedError``. This keeps the workflow
        # smoke step green before tickets #1 and #4 ship.
        result = triage.handle_issue(self.payload, "fake-key-for-smoke")
        self.assertEqual(
            result,
            {"status": "pending", "reason": "downstream_not_implemented"},
        )


if __name__ == "__main__":
    unittest.main()
