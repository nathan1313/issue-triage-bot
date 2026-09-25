# issue-triage-bot

A GitHub Actions bot that triages new and edited issues in this
repository.

## Triage Bot

The bot runs via `.github/workflows/triage.yml`, which fires on
`issues.opened` and `issues.edited` events. The workflow checks out
the repo, sets up Python 3.11, and invokes the entry point in
`.github/triage.py` (`handle_issue`). The bootstrap handler is
intentionally a no-op that exits cleanly until the downstream
tickets land.

### Required secrets

| Secret             | Purpose                                        | Required yet? |
| ------------------ | ---------------------------------------------- | ------------- |
| `TYPESAFE_API_KEY` | API key for the Jev classifier (issue #1)      | No — the workflow skips classification gracefully while it is absent. |

Set the secret under **Settings → Secrets and variables → Actions**.

### Related tickets

- Issue #1 — Jev classifier client (`classify`), depends on this bootstrap.
- Label-apply ticket — applies labels derived from the classification.
- Comment-post ticket — `format_response` and comment posting.

### Local verification

```sh
python -m unittest tests.test_triage_smoke
python -c "import yaml; yaml.safe_load(open('.github/workflows/triage.yml'))"
```
