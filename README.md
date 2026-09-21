# issue-triage-bot

A GitHub Actions bot that auto-triages incoming issues using
[TypeSafe AI's Jev decision model][jev]. Classifies each new
issue by category, automatable-vs-needs-human, and urgency,
then applies labels and posts a confirmation comment.

[jev]: https://vercel.com/i/what-is-jev

## What it does

When a new issue is opened in this repo:

1. The Action fires on `issues.opened` (and `issues.reopened`)
2. It builds a compact "state" dict from the issue (title, body,
   labels, comment count)
3. It calls Jev with three typed questions:
   - `category` — bug / feature / question / docs / spike / chore
   - `is_automatable` — can a coder reasonably tackle this without
     a human in the loop, or does it need judgment first?
   - `urgency` — score 0 (can wait weeks) → 2 (blocking users today)
4. Applies labels (`bot:category/bug`, `bot:automatable`, etc.)
5. Posts a short confirmation comment with the classification

## Quick start

```yaml
# .github/workflows/triage.yml in your repo
name: triage
on:
  issues:
    types: [opened, reopened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: nathan1313/issue-triage-bot@v1
        with:
          typesafe_api_key: ${{ secrets.TYPESAFE_API_KEY }}
```

Set `TYPESAFE_API_KEY` in your repo's Settings → Secrets and
you're done. The first classification arrives within a few
seconds of the issue opening.

## Why a separate project

This bot is the integration target for an orchestrator-driven
demo of "the orchestrator building the bot that demonstrates
itself." The bot's first ticket — once the orchestrator picks
it up — will be to wire Jev into the orchestrator's own
classifier as a tiebreaker. See the project board for that
ticket.

## Development

```bash
# Run a one-shot classification against a local file
pip install -r requirements.txt
TYPESAFE_API_KEY=*** python -m triage_bot \
    --input tests/fixtures/sample-issue.json
```

The `--dry-run` flag prints the Jev decision without posting
labels or comments — useful for testing the question pack.

## License

MIT — see [LICENSE](./LICENSE).

## Status

v0.1 scaffold (this commit). Jev client lands in the next PR.
