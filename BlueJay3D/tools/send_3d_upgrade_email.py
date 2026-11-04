#!/usr/bin/env python3
"""
send_3d_upgrade_email.py
Sends the SpeedyBee F405 AIO 3D Upgrade package & guide directly to your email.
Uses OAuth2 with automatic local browser approval, then saves the token to ~/.config/bf3d-automation/token_sendmail.json.
"""

import os
import sys
import mimetypes
import argparse
from pathlib import Path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose"
]

CONF = Path.home() / ".config" / "bf3d-automation"
CLIENT_SECRET = Path("/home/admin/Documents/NAWA/Project Organizational Files/tools/credentials.json")
TOKEN_FILE = CONF / "token_nawa_sendmail.json"

DEFAULT_TO = "zoestumbaugh@gmail.com"
SUBJECT = "SpeedyBee F405 AIO - 3D Upgrade Package, Guide & CLI Dump"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception:
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json())
            os.chmod(TOKEN_FILE, 0o600)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if not CLIENT_SECRET.exists():
            raise FileNotFoundError(f"Missing OAuth client secret at {CLIENT_SECRET}")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        CONF.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
        os.chmod(TOKEN_FILE, 0o600)

    return creds


def send_email(to_addr: str, files: list):
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    msg = EmailMessage()
    msg["To"] = to_addr
    msg["From"] = "me"
    msg["Subject"] = SUBJECT

    guide_path = Path("/mnt/storage/media/3D Whoop/backups/SpeedyBee_F405_AIO/HOW_TO_UPGRADE_SPEEDYBEE_F405_AIO_3D.md")
    guide_text = guide_path.read_text() if guide_path.exists() else "SpeedyBee F405 AIO 3D Upgrade Guide"

    cli_path = Path("/mnt/storage/media/3D Whoop/SPEEDYBEEF405AIO_3D_Edition_Restore_CLI.txt")
    cli_snippet = cli_path.read_text()[:1200] if cli_path.exists() else ""

    body = f"""Hi Zoe,

Here is your complete 3D upgrade package for the SpeedyBee F405 AIO (SPEEDYBEEF405AIO).

All files and instructions are attached to this email.

========================================================================
QUICK SUMMARY
========================================================================
- Flight Controller: BetaFlight 3D Edition v0.3.1-test (SPEEDYBEEF405AIO)
- ESC Target: BlueJay3D v0.22.0-3D (J_H_40, 48 kHz / 24 kHz / 96 kHz)
- 3D Edition Parameters: 3d_iterm_mode = PER_DIRECTION, 3d_dyn_idle = ON (min 5000 RPM)
- Receiver: CRSF on UART6 (serial 5 64)
- Motor Poles: 14

Attached Files:
1. SpeedyBee_F405_AIO_3D_Upgrade_Package.zip (All .hex binaries + CLI restore + raw dumps)
2. HOW_TO_UPGRADE_SPEEDYBEE_F405_AIO_3D.md (Full step-by-step guide)
3. SPEEDYBEEF405AIO_3D_Edition_Restore_CLI.txt (1-Click paste for Betaflight CLI)

========================================================================
STEP-BY-STEP GUIDE
========================================================================
{guide_text}
"""
    msg.set_content(body)

    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            print(f"Skipping non-existent file: {path}")
            continue
        content_type, _ = mimetypes.guess_type(str(path))
        if content_type is None:
            content_type = "application/octet-stream"
        maintype, subtype = content_type.split("/", 1)

        msg.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name
        )
        print(f"Attached: {path.name} ({path.stat().st_size} bytes)")

    import base64
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    sent = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
    print("Email successfully sent! Message ID:", sent.get("id"))
    return sent


def main():
    parser = argparse.ArgumentParser(description="Send 3D Upgrade package email")
    parser.add_argument("--to", default=DEFAULT_TO, help="Recipient email address")
    args = parser.parse_args()

    pkg_dir = Path("/mnt/storage/media/3D Whoop/backups/SpeedyBee_F405_AIO")
    attachments = [
        pkg_dir / "SpeedyBee_F405_AIO_3D_Upgrade_Package.zip",
        pkg_dir / "HOW_TO_UPGRADE_SPEEDYBEE_F405_AIO_3D.md",
        Path("/mnt/storage/media/3D Whoop/SPEEDYBEEF405AIO_3D_Edition_Restore_CLI.txt"),
    ]

    send_email(args.to, attachments)


if __name__ == "__main__":
    main()
