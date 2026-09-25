# issue-triage-bot

A GitHub Actions bot that triages new and edited issues in this
repository.

## Triage Bot

The bot runs via `.github/workflows/triage.yml`, which fires on
`issues.opened` and `issues.edited` events. The workflow checks out
the repo, sets up Python 3.11, and invokes the entry point in
`.github/triage.py` (`handle_issue`).

The bot uses a thin, bot-specific Jev client (`.github/triage.py::classify()`)
to classify incoming issues with:

- **category** (choice): bug / feature / question / docs / spike / chore
- **automatable** (bool): can this be resolved without a human in the loop?
- **urgency** (int 0-2): 0 = can wait weeks, 1 = needs attention this week,
  2 = blocking users today

The client is pattern-matched after the orchestrator's `JevClient.decide()`
signature but is a separate ~50-LOC stdlib-plus-requests implementation.

### Required secrets

| Secret             | Purpose                                        | Required yet? |
| ------------------ | ---------------------------------------------- | ------------- |
| `TYPESAFE_API_KEY` | API key for the Jev classifier (issue #1)      | Yes — the bot returns `{"status": "completed", ...}` when the key is set. Without the key it returns `{"status": "skipped", "reason": "no_api_key"}`. On transport failure it returns `{"status": "skipped", "reason": "jev_unavailable"}`. |

Set the secret under **Settings → Secrets and variables → Actions**.

### Related tickets

- Issue #1 — Jev classifier client (`classify`) — **Implemented**
- Label-apply ticket — applies labels derived from the classification.
- Comment-post ticket — `format_response` and comment posting.

### Local verification

```sh
python -m unittest tests.test_triage_smoke
python -c "import yaml; yaml.safe_load(open('.github/workflows/triage.yml'))"
```
