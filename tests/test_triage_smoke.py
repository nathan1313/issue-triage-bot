"""Smoke tests for the triage bot bootstrap (issue #2).

Uses stdlib unittest only so the workflow stays hermetic (no pytest
dependency at bootstrap time).
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

import requests  # noqa: E402

# Make .github/triage.py importable without installing anything.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, ".github"))

from triage import handle_issue, classify  # noqa: E402

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
        # After issue #1, with a key present the bot runs classify
        # and returns completed on success. See
        # test_handle_issue_with_api_key_runs_classify below.


class ClassifySmokeTest(unittest.TestCase):
    """Tests for the classify() function (issue #1)."""

    def setUp(self):
        with open(_FIXTURE_PATH, encoding="utf-8") as fh:
            self.payload = json.load(fh)

    def test_classify_with_mocked_jev(self):
        """Patches requests.post to return a canned Jev response,
        asserts the typed result."""
        canned_response = {
            "answers": {
                "category": {"value": "bug"},
                "automatable": {"value": False},
                "urgency": {"value": 2},
            }
        }

        with patch("triage.requests.post") as mock_post:
            mock_post.return_value.json.return_value = canned_response
            mock_post.return_value.raise_for_status = lambda: None

            result = classify(self.payload, "fake-api-key")

        self.assertEqual(result.category, "bug")
        self.assertEqual(result.automatable, False)
        self.assertEqual(result.urgency, 2)
        mock_post.assert_called_once()

    def test_classify_transport_error_falls_back(self):
        """Patches requests.post to raise a RequestException, asserts
        handle_issue returns skipped with reason=jev_unavailable."""
        with patch("triage.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Connection refused")

            result = handle_issue(self.payload, "fake-api-key")

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "jev_unavailable")

    def test_handle_issue_with_api_key_runs_classify(self):
        """Patches Jev to a happy-path canned response, asserts the bot
        returns {"status": "completed", ...} with the expected fields."""
        canned_response = {
            "answers": {
                "category": {"value": "feature"},
                "automatable": {"value": True},
                "urgency": {"value": 1},
            }
        }

        with patch("triage.requests.post") as mock_post:
            mock_post.return_value.json.return_value = canned_response
            mock_post.return_value.raise_for_status = lambda: None

            result = handle_issue(self.payload, "fake-api-key")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["category"], "feature")
        self.assertEqual(result["automatable"], True)
        self.assertEqual(result["urgency"], 1)
        self.assertIsNone(result["reason"])


if __name__ == "__main__":
    unittest.main()
