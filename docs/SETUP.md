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

## 3. Gmail, one-time (about ten minutes)

The monitor sends mail as you, to you, through the Gmail API with OAuth. No app passwords.

1. **Create a Google Cloud project.** https://console.cloud.google.com → project picker →
   *New project* → name it `sovereign-debt-monitor` → Create.
2. **Enable the Gmail API.** In that project: *APIs & Services → Library* → search
   "Gmail API" → Enable.
3. **Configure the OAuth consent screen.** *APIs & Services → OAuth consent screen*
   (Google now calls this *Google Auth Platform → Branding/Audience*):
   - User type: **External**. App name: `Sovereign Debt Monitor`. Support email: yours.
   - Audience: leave the app in **Testing** and add `danielconorsims@gmail.com` as a test
     user. (Publishing is not needed; testing mode is fine for a single user. Note: in
     testing mode refresh tokens expire after 7 days *unless* the app's publishing status is
     set to "In production". If the token keeps expiring, click *Publish app*; no
     verification is required for the `gmail.send` scope used by a single user, Google only
     shows a warning screen once.)
   - Scopes: add `https://www.googleapis.com/auth/gmail.send`.
4. **Create credentials.** *APIs & Services → Credentials → Create credentials → OAuth
   client ID* → Application type **Desktop app** → name `sdm-local` → Create → **Download
   JSON**. Save it as `.secrets/credentials.json` in the repo (gitignored).
5. **Authorise once, on your machine:**
   ```
   .venv/bin/sdm email --dry-run      # sanity: writes reports/outbox/*.eml, no Google call
   .venv/bin/sdm email                # opens a browser, you approve, token saved to .secrets/token.json
   ```
   The first real send is the one in phase 7 of the build; after that the token refreshes
   itself.
6. **GitHub Actions.** Copy the two files into repository secrets so the scheduled runs can
   send: *Settings → Secrets and variables → Actions → New repository secret*:
   - `GMAIL_CREDENTIALS_JSON` = the full contents of `.secrets/credentials.json`
   - `GMAIL_TOKEN_JSON` = the full contents of `.secrets/token.json`
   - `ANTHROPIC_API_KEY`, and optionally `FRED_API_KEY`.

   When the token is refreshed in CI the new refresh token is not written back to the
   secret (refresh tokens do not rotate for Google desktop clients, so this is fine).

## 4. Schedules

`.github/workflows/quarterly.yml` runs on the 15th of January, April, July and October;
`monthly.yml` on the 15th of the other months and only sends mail if a transition or a
1.5σ move fired. Both can be started by hand from the Actions tab (*Run workflow*). Each run
commits refreshed data and reports back to the branch it ran on.
