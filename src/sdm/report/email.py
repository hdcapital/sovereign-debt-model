"""Send the quarterly (or monthly alert) email from your Gmail account.

Two transports, picked automatically:

* **App password over SMTP** (simplest): set ``GMAIL_APP_PASSWORD`` (the 16-character
  password from Google Account -> Security -> 2-Step Verification -> App passwords) and
  optionally ``GMAIL_USER`` (defaults to the owner email in config/report.yaml).
* **Gmail API with OAuth2** (fallback when no app password is set): .secrets/credentials.json
  and .secrets/token.json, or in CI the GMAIL_CREDENTIALS_JSON / GMAIL_TOKEN_JSON variables.

--dry-run writes the complete RFC 822 message to reports/outbox/ instead of sending.
"""

from __future__ import annotations

import base64
import json
import logging
import mimetypes
import os
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from sdm.config import load_report_config
from sdm.paths import ROOT, SECRETS

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS = SECRETS / "credentials.json"
TOKEN = SECRETS / "token.json"
OUTBOX = ROOT / "reports" / "outbox"


def build_message(
    subject: str, html_body: str, attachments: list[Path], to: str, sender: str = "me"
) -> EmailMessage:
    msg = EmailMessage()
    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    msg.set_content("This report is HTML; please view it in an HTML-capable client.")
    msg.add_alternative(html_body, subtype="html")
    for path in attachments:
        if not path.exists():
            log.warning("attachment missing: %s", path)
            continue
        ctype, _ = mimetypes.guess_type(str(path))
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
    return msg


def _credentials() -> object:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    SECRETS.mkdir(parents=True, exist_ok=True)
    env_token = os.environ.get("GMAIL_TOKEN_JSON")
    if env_token and not TOKEN.exists():
        TOKEN.write_text(env_token, encoding="utf-8")
    env_creds = os.environ.get("GMAIL_CREDENTIALS_JSON")
    if env_creds and not CREDENTIALS.exists():
        CREDENTIALS.write_text(env_creds, encoding="utf-8")
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    if not creds or not creds.valid:
        if not CREDENTIALS.exists():
            raise RuntimeError("no .secrets/credentials.json; follow docs/SETUP.md (Gmail) first")
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
        log.info("token saved to %s", TOKEN)
    return creds


def _send_smtp(msg: EmailMessage, user: str, app_password: str) -> str:
    """Gmail SMTP with an app password. Returns the message id Gmail assigned, if any."""
    msg.replace_header("From", user) if msg["From"] else msg.__setitem__("From", user)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as smtp:
        smtp.login(user, app_password.replace(" ", ""))
        smtp.send_message(msg)
    log.info("sent via SMTP as %s", user)
    return msg.get("Message-ID", "sent")


def send(msg: EmailMessage, dry_run: bool) -> Path | str:
    if dry_run:
        OUTBOX.mkdir(parents=True, exist_ok=True)
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in msg["Subject"])[:80]
        path = OUTBOX / f"{date.today().isoformat()}-{safe}.eml"
        path.write_bytes(bytes(msg))
        log.info("dry run: wrote %s (%d KB)", path, path.stat().st_size // 1024)
        return path
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    if app_password:
        user = os.environ.get("GMAIL_USER", "").strip() or load_report_config()["owner_email"]
        return _send_smtp(msg, user, app_password)
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=_credentials(), cache_discovery=False)
    raw = base64.urlsafe_b64encode(bytes(msg)).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    log.info("sent message id %s", result.get("id"))
    return str(result.get("id"))


def send_quarterly(period: str, dry_run: bool = False) -> Path | str:
    cfg = load_report_config()
    html = (ROOT / "reports" / "quarterly" / f"{period}.html").read_text(encoding="utf-8")
    attachments = [ROOT / p for p in cfg["email"]["attachments"]]
    subject = cfg["subject_template"].format(period=period)
    msg = build_message(subject, html, attachments, to=cfg["owner_email"])
    return send(msg, dry_run)


def send_alert(period: str, body_html: str, dry_run: bool = False) -> Path | str:
    cfg = load_report_config()
    subject = cfg["subject_template"].format(period=period) + " — monthly alert"
    attachments = [
        ROOT / "reports" / "dashboard" / "latest.html",
        ROOT / "data" / "clean" / "indicators_latest.csv",
    ]
    msg = build_message(subject, body_html, attachments, to=cfg["owner_email"])
    return send(msg, dry_run)


def secrets_status() -> dict[str, bool]:
    return {
        "app_password": bool(os.environ.get("GMAIL_APP_PASSWORD")),
        "credentials.json": CREDENTIALS.exists() or bool(os.environ.get("GMAIL_CREDENTIALS_JSON")),
        "token.json": TOKEN.exists() or bool(os.environ.get("GMAIL_TOKEN_JSON")),
        "token_env_is_json": _is_json(os.environ.get("GMAIL_TOKEN_JSON")),
    }


def _is_json(s: str | None) -> bool:
    if not s:
        return False
    try:
        json.loads(s)
        return True
    except ValueError:
        return False
