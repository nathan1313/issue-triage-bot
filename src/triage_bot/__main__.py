"""Entry point for the triage-bot Action.

Reads GITHUB_EVENT_PATH, GITHUB_REPOSITORY, and GITHUB_ISSUE_NUMBER
from env (set by the Action runner), fetches the issue, and
applies the bot:received label + a confirmation comment.

In v0.1 the bot does NO classification — that's PR B's work
(Jev client + question pack). This PR's contract is just:
"the bot runs on issues.opened, doesn't crash, and leaves a
trace."

Supports --dry-run for local testing without posting to GitHub.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from . import __version__


def _read_event() -> dict:
    """Read the GITHUB_EVENT_PATH payload (or a local --input file)."""
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        raise SystemExit(
            "GITHUB_EVENT_PATH not set or file missing — "
            "this entry point is meant to run inside a GitHub Action. "
            "For local testing, pass --input <path>."
        )
    with open(path) as f:
        return json.load(f)


def _read_input(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _post_comment(repo: str, issue_number: int, body: str,
                  *, github_token: str) -> None:
    """POST a comment via the GitHub REST API.

    Issues a comment with the given body. Raises on non-2xx so
    the Action step fails loudly if the comment doesn't land.
    """
    import requests
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": body},
        timeout=15,
    )
    resp.raise_for_status()


def _apply_label(repo: str, issue_number: int, label: str,
                 *, github_token: str) -> None:
    """Add a single label to an issue (idempotent: 422 if already present is fine)."""
    import requests
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"labels": [label]},
        timeout=15,
    )
    # 422 = label already exists; that's fine for an idempotent op.
    if resp.status_code not in (200, 201, 422):
        resp.raise_for_status()


def _build_comment(issue: dict) -> str:
    """The v0.1 comment body. PR B replaces this with the Jev-classified version."""
    title = issue.get("title", "(no title)")
    return (
        "👋 Thanks for opening this issue. "
        f"I've recorded it as `{title[:80]}` and a maintainer "
        "will pick it up shortly.\n\n"
        "_This comment was posted by `issue-triage-bot` v"
        f"{__version__}. Next iteration will auto-classify the issue._"
    )


def run_from_action() -> int:
    """Called from inside the GitHub Action (no CLI args)."""
    event = _read_event()
    issue = event.get("issue") or {}
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    issue_number = issue.get("number")
    github_token = os.environ.get("GITHUB_TOKEN", "")

    if not (repo and issue_number and github_token):
        raise SystemExit(
            "Missing GITHUB_REPOSITORY / issue.number / GITHUB_TOKEN. "
            f"Got repo={repo!r} issue_number={issue_number!r} "
            f"token={'set' if github_token else 'unset'}."
        )

    body = _build_comment(issue)
    _post_comment(repo, issue_number, body, github_token=github_token)
    _apply_label(repo, issue_number, "bot:received", github_token=github_token)

    # GitHub Actions picks up `::set-output` style if you write to
    # $GITHUB_OUTPUT in newer runners. The outputs in action.yml
    # are reserved for PR B (when Jev fills them in).
    print(f"triage-bot v{__version__}: labeled and commented on "
          f"{repo}#{issue_number}")
    return 0


def run_local(args: argparse.Namespace) -> int:
    """Called via the CLI for local testing."""
    payload = _read_input(args.input)
    issue = payload.get("issue") or payload
    body = _build_comment(issue)
    if args.dry_run:
        print("DRY RUN — would post:")
        print(json.dumps({"body": body, "labels": ["bot:received"]},
                         indent=2))
        return 0
    # Real local mode requires --repo + --issue-number + --token.
    repo = args.repo
    issue_number = args.issue_number
    github_token = args.token
    if not (repo and issue_number and github_token):
        print("ERROR: --repo, --issue-number, and --token required for "
              "non-dry-run local mode.", file=sys.stderr)
        return 2
    _post_comment(repo, issue_number, body, github_token=github_token)
    _apply_label(repo, issue_number, "bot:received", github_token=github_token)
    print(f"Posted comment + label to {repo}#{issue_number}")
    return 0


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="triage_bot",
        description="issue-triage-bot: auto-triage incoming GitHub issues.",
    )
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {__version__}")
    p.add_argument("--input", default=None,
                   help="Local path to a GitHub event payload JSON. "
                        "Required for local testing; ignored inside the Action.")
    p.add_argument("--repo", default=None,
                   help="owner/repo for local real-mode testing.")
    p.add_argument("--issue-number", type=int, default=None,
                   help="Issue number for local real-mode testing.")
    p.add_argument("--token", default=None,
                   help="GitHub token for local real-mode testing.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be posted without contacting GitHub.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    # If running inside an Action, GITHUB_EVENT_PATH is set and
    # we don't expect CLI args. Otherwise parse argv and dispatch.
    if os.environ.get("GITHUB_EVENT_PATH") and not argv:
        return run_from_action()
    args = build_argparser().parse_args(argv)
    if not args.input:
        build_argparser().error(
            "--input is required (or run inside a GitHub Action)."
        )
    return run_local(args)


if __name__ == "__main__":
    sys.exit(main())
