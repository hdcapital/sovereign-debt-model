# Setup

## 1. Local

```
git clone <repo> && cd sovereign-debt-model
make setup                     # venv, package + dev + report extras, .env from template
make test                      # unit tests (no network)
.venv/bin/sdm check            # validates config
```

Data pulls need outbound HTTPS to the hosts in `docs/DATA_SOURCES.md`. From a clean clone
the repo already carries the latest committed data, so `make indicators`, `make backtest`
and `make dashboard` work offline.

## 2. API keys (`.env`, never committed)

| Key | Needed for | Where to get it |
|---|---|---|
| `FRED_API_KEY` | optional: FRED JSON API instead of the keyless CSV export | https://fred.stlouisfed.org/docs/api/api_key.html (free, instant) |
| `ANTHROPIC_API_KEY` | `make report` (narrative) | https://console.anthropic.com/settings/keys |

## 3. Gmail (two minutes, app password)

1. Your Google account needs 2-Step Verification on: https://myaccount.google.com/security.
2. Open https://myaccount.google.com/apppasswords, type a name such as `sovereign-debt-monitor`,
   click Create. Google shows a 16-character password once; copy it (spaces do not matter).
3. Locally: put it in `.env` as `GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx`. Then
   `.venv/bin/sdm email --dry-run` (writes `reports/outbox/*.eml`, no send) and
   `.venv/bin/sdm email` (real send to the owner address).
4. GitHub: repository → Settings → Secrets and variables → Actions → New repository secret,
   name `GMAIL_APP_PASSWORD`, value the 16 characters. Add `ANTHROPIC_API_KEY` the same way
   (and optionally `GMAIL_USER` if the sending account is not the owner address, and `FRED_API_KEY`).

If an app password ever stops working, Google has either turned off 2-Step Verification
or revoked it; create a new one. The OAuth route below is the alternative if your Google
Workspace admin blocks app passwords.

### Alternative: Gmail API with OAuth

Create a Google Cloud project, enable the Gmail API, configure the consent screen (External,
yourself as test user, scope `gmail.send`), create a Desktop OAuth client and save its JSON as
`.secrets/credentials.json`. Run `.venv/bin/sdm email` once; the browser flow saves
`.secrets/token.json`. In GitHub add `GMAIL_CREDENTIALS_JSON` and `GMAIL_TOKEN_JSON` with the
full contents of each file. The sender uses OAuth only when `GMAIL_APP_PASSWORD` is unset.

## 4. Recipient

The report goes to `owner_email` in `config/report.yaml`. To send somewhere else without
editing the file: set `OWNER_EMAIL=someone@example.com` in `.env` (locally) or as a
repository secret named `OWNER_EMAIL` (GitHub Actions), or pass `--to` for a one-off:
`.venv/bin/sdm email --to someone@example.com`. The sending account is still the Gmail
account whose app password you configured.

## 5. Schedules

`.github/workflows/quarterly.yml` runs on the 15th of January, April, July and October;
`monthly.yml` on the 15th of the other months and only sends mail if a transition or a
1.5σ move fired. Both can be started by hand from the Actions tab (*Run workflow*). Each run
commits refreshed data and reports back to the branch it ran on.
