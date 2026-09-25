# issue-triage-bot

A GitHub Actions bot for triaging incoming issues.

This repo is intentionally minimal. It's a target for an
orchestrator-driven demo: the orchestrator will build the bot
from scratch against the open issues here.

## Triage Bot

The bot lives in `.github/workflows/triage.yml` and runs on every
`issues.opened` and `issues.edited` event against this repository.
It is implemented in Python 3.11 (no Node step) so it shares a
single toolchain with the orchestrator's venv.

The Python entry point is `.github/triage.py`, which exposes:

- `handle_issue(event_payload, api_key)` — the action-facing dispatcher.
  It tolerates a missing `TYPESAFE_API_KEY` by returning
  `{"status": "skipped", "reason": "no_api_key"}`, and short-circuits
  to `{"status": "pending", "reason": "downstream_not_implemented"}`
  while the classifier and comment tickets are still open.
- `classify(event_payload)` — stub; lands in the Jev classifier ticket.
- `format_response(classification)` — stub; lands in the comment-post ticket.

### Required secrets

| Secret              | Purpose                                                       | Required for #2? |
| ------------------- | ------------------------------------------------------------- | ---------------- |
| `TYPESAFE_API_KEY`  | Auth for the downstream classifier service (tickets #1, #3).   | No (tolerated)   |

`GITHUB_TOKEN` is used directly — no PAT, no bot account.

### Related tickets

- [#1](../issues/1) — Add a Jev-based classifier (depends on #2).
- #3 — Apply labels to issues (depends on #2).
- #4 — Post triage comments (depends on #2).

### Local verification

```bash
python -m unittest tests.test_triage_smoke
python -c "import yaml; yaml.safe_load(open('.github/workflows/triage.yml'))"
python -m py_compile .github/triage.py
```

## Open issues

- [#1](../issues/1) — Add a Jev-based classifier for new issues.

## License

MIT — see [LICENSE](./LICENSE).
