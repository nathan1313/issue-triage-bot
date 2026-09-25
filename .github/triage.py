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

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


# ---------------------------------------------------------------------------
# Thin bot-specific Jev client
# ---------------------------------------------------------------------------
# Pattern-matched after orchestrator's JevClient.decide() signature
# (POST /v1/systemone with {model, state, questions}) but is a separate
# ~50-LOC implementation that stays within the bot's stateless,
# single-call-per-event model.
# ---------------------------------------------------------------------------

_JEV_API_URL = "https://api.typesafe.ai/v1/systemone"
_JEV_MODEL = "jev-classifier-v1"


@dataclass
class ClassificationResult:
    """Typed result from the Jev classifier."""

    category: str
    automatable: bool
    urgency: int


def _build_jev_payload(event_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build the Jev API payload from a GitHub issue event payload."""
    issue = event_payload.get("issue", {})
    title = issue.get("title", "")
    body = issue.get("body", "")
    combined_text = f"{title}\n\n{body}".strip()

    questions: List[Dict[str, Any]] = [
        {
            "id": "category",
            "type": "choice",
            "question": "What is the category of this GitHub issue?",
            "options": ["bug", "feature", "question", "docs", "spike", "chore"],
        },
        {
            "id": "automatable",
            "type": "noul",
            "question": "Can this issue be resolved without a human in the loop?",
        },
        {
            "id": "urgency",
            "type": "score",
            "question": "What is the urgency of this issue? 0 = can wait weeks, 1 = needs attention this week, 2 = blocking users today",
            "min": 0,
            "max": 2,
        },
    ]

    return {
        "model": _JEV_MODEL,
        "state": combined_text,
        "questions": questions,
    }


def classify(event_payload: Dict[str, Any], api_key: Optional[str] = None) -> ClassificationResult:
    """Classify an issue payload using the Jev classifier.

    Calls the Jev API with three questions:
    - category (choice): bug / feature / question / docs / spike / chore
    - automatable (noul): is this automatable without a human in the loop?
    - urgency (score): 0 (can wait weeks) to 2 (blocking users today)

    Raises:
        ValueError: If the Jev API returns an unexpected response shape.
        requests.RequestException: On transport errors.

    Returns:
        ClassificationResult with category, automatable, and urgency fields.
    """
    if not api_key:
        raise ValueError("TYPESAFE_API_KEY is required for classification")

    payload = _build_jev_payload(event_payload)

    response = requests.post(
        _JEV_API_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    answers = data.get("answers", {})

    category = answers.get("category", {}).get("value", "question")
    automatable_value = answers.get("automatable", {}).get("value", False)
    urgency = int(answers.get("urgency", {}).get("value", 0))

    return ClassificationResult(
        category=category,
        automatable=bool(automatable_value),
        urgency=urgency,
    )


# ---------------------------------------------------------------------------
# Bot entry point
# ---------------------------------------------------------------------------


def handle_issue(
    event_payload: Dict[str, Any], api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Handle an ``issues.opened``/``issues.edited`` event payload.

    Never raises:
    - Without an API key it reports a skip (no_api_key).
    - On transport failure it reports a skip (jev_unavailable).
    - On successful classification it reports completed with the result.
    """
    if not api_key:
        return {"status": "skipped", "reason": "no_api_key"}

    try:
        result = classify(event_payload, api_key)
        return {
            "status": "completed",
            "category": result.category,
            "automatable": result.automatable,
            "urgency": result.urgency,
            "reason": None,
        }
    except requests.RequestException:
        return {"status": "skipped", "reason": "jev_unavailable"}
    except ValueError:
        # Raised when API key is missing (handled above), but kept for safety
        return {"status": "skipped", "reason": "no_api_key"}


def format_response(classification: str) -> str:
    """Format the bot comment. Reserved for the comment-post ticket."""
    raise NotImplementedError("format_response is implemented by the comment-post ticket")
