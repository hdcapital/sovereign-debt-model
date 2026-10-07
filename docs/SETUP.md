# Setup

## Local (phase 1)

```
git clone <repo> && cd sovereign-debt-model
make setup          # creates .venv, installs package + dev + report extras, copies .env.example
# edit .env: FRED_API_KEY, ANTHROPIC_API_KEY
make test
```

## API keys

- **FRED**: free key at https://fred.stlouisfed.org/docs/api/api_key.html → `FRED_API_KEY` in `.env`.
- **Anthropic**: `ANTHROPIC_API_KEY` in `.env` (used only by `make report`).

## Gmail OAuth (phase 7, to be written)

One-time Google Cloud project, OAuth consent screen, desktop-app credentials, first-run token
exchange. `credentials.json` and `token.json` go in `.secrets/` (gitignored). The GitHub Actions
workflow reads the token from a repo secret. Full walkthrough lands with phase 7.

## GitHub Actions (phase 8, to be written)

Secrets: `FRED_API_KEY`, `ANTHROPIC_API_KEY`, `GMAIL_TOKEN_JSON`, `GMAIL_CREDENTIALS_JSON`.
