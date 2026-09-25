"""Bootstrap entry point for the issue-triage-bot.

Ticket #2 ships only the runtime shell: the handler tolerates a
missing ``TYPESAFE_API_KEY`` (returns a sentinel ``skipped`` response),
and the ``classify`` / ``format_response`` helpers are stubs that
downstream tickets (#1 / #3 / #4) will replace. The handler must
short-circuit on both the no-key path AND the no-downstream-implemented
path so that the smoke step stays green until the classifier and
comment tickets land.
"""

from __future__ import annotations

from typing import Any


def handle_issue(event_payload: dict, api_key: str | None) -> dict:
    """Dispatch triage work for an ``issues.opened`` / ``issues.edited`` event.

    Returns a sentinel dict describing what (if anything) the bot did.
    Downstream tickets will replace the body, but the contract here is:
    * If ``api_key`` is ``None``, return ``{"status": "skipped", "reason": "no_api_key"}``.
    * If the classifier / formatter are not yet implemented (ticket #1 / #4
      haven't landed), return ``{"status": "pending", "reason": "downstream_not_implemented"}``.
    """
    if api_key is None:
        return {"status": "skipped", "reason": "no_api_key"}

    try:
        classification = classify(event_payload)
        response = format_response(classification)
    except NotImplementedError:
        return {"status": "pending", "reason": "downstream_not_implemented"}

    return {"status": "ok", "classification": classification, "response": response}


def classify(event_payload: dict) -> str:
    """Stub — replaced by the Jev-based classifier (ticket #1)."""
    raise NotImplementedError("classify lands in ticket #1")


def format_response(classification: str) -> str:
    """Stub — replaced by the comment-formatter ticket (#4)."""
    raise NotImplementedError("format_response lands in ticket #4")
