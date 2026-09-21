"""triage_bot — auto-triage incoming GitHub issues.

v0.1 scaffold: applies a `bot:received` label and posts a
short "thanks for opening this" comment. Jev classification
lands in the next PR.

Public entry point is `triage_bot.__main__:main`, invoked by
the GitHub Action composite step (see action.yml).
"""
from __future__ import annotations

__version__ = "0.1.0"
