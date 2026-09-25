"""Issue triage bot entry point.

Bootstrap for issue #2. The classification and response-formatting
stages are intentionally left as stubs; they are filled in by the
downstream tickets:

- issue #1: Jev classifier client (``classify``)
- label-apply ticket: applies labels derived from the classification
- comment-post ticket: ``format_response`` + comment posting

The handler is deliberately tolerant of a missing API key so the
workflow smoke step exits green before any secrets are configured.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def handle_issue(
    event_payload: Dict[str, Any], api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Handle an ``issues.opened``/``issues.edited`` event payload.

    Never raises on the bootstrap path: without an API key it reports
    a skip, and with a key it reports pending until the downstream
    tickets (#1, label-apply, comment-post) land.
    """
    if not api_key:
        return {"status": "skipped", "reason": "no_api_key"}
    return {"status": "pending", "reason": "downstream_not_implemented"}


def classify(event_payload: Dict[str, Any]) -> str:
    """Classify an issue payload. Reserved for issue #1 (Jev client)."""
    raise NotImplementedError("classify is implemented by issue #1")


def format_response(classification: str) -> str:
    """Format the bot comment. Reserved for the comment-post ticket."""
    raise NotImplementedError("format_response is implemented by the comment-post ticket")
