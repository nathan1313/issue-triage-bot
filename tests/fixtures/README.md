# Test fixtures

- `sample-issue.json` — minimal `issues.opened` event payload shaped
  like what `GITHUB_EVENT_PATH` will contain when the Action fires.
  Pass it to `python -m triage_bot --input tests/fixtures/sample-issue.json --dry-run`.

PR B will add:
- `jev-success.json` — canned Jev response (a `bug` classification)
- `jev-low-confidence.json` — canned Jev response with conf < threshold
