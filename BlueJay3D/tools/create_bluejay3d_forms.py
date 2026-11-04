#!/usr/bin/env python3
r"""
Create the two official Google Forms for BlueJay3D (modeled after BetaFlight 3D Edition):
  1. BlueJay3D: Request a Build for Your ESC / Board
  2. BlueJay3D: Log & Feedback Upload (with 10-file .BBL upload & 5-file config/screenshot upload)

How it works:
  - Uses OAuth credentials from ~/.config/bf3d-automation/client_secret.json
  - Creates the Target Request Form via Google Forms API v1 (forms.create + forms.batchUpdate)
  - Copies the BetaFlight 3D Edition Log Upload Form (1FogE8pFKXeIBI9-ypMe_yrfEz8o_IOBFzjttj1RJlRg)
    via Google Drive API v3 (drive.files.copy) so the two Google Forms FileUploadQuestion items
    (.BBL logs up to 10 files / 100 MB, plus screenshots/configs up to 5 files) are preserved,
    and then updates all titles, descriptions, and questions for BlueJay3D via forms.batchUpdate.
  - Automatically updates all markdown links in Drones/BlueJay3D/*.md and Drones/README.md.

Usage:
  /mnt/storage/media/3D\ Whoop/3d-whoop-tuning/.venv/bin/python tools/create_bluejay3d_forms.py
"""

import argparse
import json
import os
import socket
import sys
from pathlib import Path

CONF = Path.home() / ".config" / "bf3d-automation"
CLIENT = CONF / "client_secret.json"
ADMIN_TOKEN = CONF / "token_bluejay3d_forms.json"
BF3D_LOG_FORM_ID = "1FogE8pFKXeIBI9-ypMe_yrfEz8o_IOBFzjttj1RJlRg"

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive",
]

DRONES_ROOT = Path("/mnt/storage/media/3D Whoop/Drones")
BJ3D_DIR = DRONES_ROOT / "BlueJay3D"
FORMS_CONFIG_OUT = BJ3D_DIR / "tools" / "forms_config.json"


def get_credentials(timeout_sec: int = 0):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if ADMIN_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(ADMIN_TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        ADMIN_TOKEN.write_text(creds.to_json())
        os.chmod(ADMIN_TOKEN, 0o600)
    if not creds or not creds.valid:
        if not CLIENT.exists():
            raise FileNotFoundError(f"Missing OAuth client secret at {CLIENT}")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
        creds = flow.run_local_server(
            port=0,
            open_browser=True,
            timeout_seconds=timeout_sec if timeout_sec > 0 else None,
        )
        CONF.mkdir(parents=True, exist_ok=True)
        ADMIN_TOKEN.write_text(creds.to_json())
        os.chmod(ADMIN_TOKEN, 0o600)
    return creds


def create_target_request_form(forms_service) -> dict:
    """Create BlueJay3D: Request a Build for Your ESC / Board."""
    created = forms_service.forms().create(
        body={
            "info": {
                "title": "BlueJay3D: Request a Build for Your ESC / Board",
                "documentTitle": "BlueJay3D - ESC Target & Board Build Request",
            }
        }
    ).execute()
    form_id = created["formId"]

    description = (
        "Want to test BlueJay3D on an 8-bit ESC or AIO flight controller that isn't in the list yet "
        "(or not sure which ESC layout your board uses)? Tell us your board/ESC and we'll identify or "
        "build a test firmware for it. When it's ready, it gets added to TARGETS.md and we'll contact you.\n\n"
        "Check the download list first; 115 firmware builds across 45 ESC layouts (EFM8BB1, EFM8BB2, and "
        "EFM8BB51 at 24/48/96 kHz) are already built. Project page, guide and downloads: "
        "https://github.com/BlindingBright/Drones/tree/bluejay3d/BlueJay3D\n\n"
        "Tip: in esc-configurator.com or the Bluejay3D Configurator, click Read Settings. "
        "The 5-character ESC layout code is shown on each ESC (e.g. O_H_5, Z_H_30, A_H_5, G_H_30, or A_X_5)."
    )

    questions_spec = [
        {
            "title": "Pilot name / callsign",
            "question": {"required": True, "textQuestion": {}},
        },
        {
            "title": "How should we contact you when your build is ready? (Discord name or email)",
            "question": {"required": True, "textQuestion": {}},
        },
        {
            "title": "ESC layout code, exactly as esc-configurator.com shows it (e.g. O_H_5, Z_H_30, B_X_30, or 'Not sure')",
            "question": {"required": True, "textQuestion": {}},
        },
        {
            "title": "AIO Flight Controller or 4-in-1 ESC manufacturer and product name (a link to the board is great)",
            "question": {"required": True, "textQuestion": {}},
        },
        {
            "title": "What kind of ESC hardware is it?",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "Built into the board (AIO / whoop / toothpick board)"},
                        {"value": "Separate 4-in-1 ESC"},
                        {"value": "Four individual ESCs"},
                        {"value": "Not sure"},
                    ],
                },
            },
        },
        {
            "title": "Current ESC firmware and MCU type",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "Bluejay (EFM8BB21 / _H_ layout)"},
                        {"value": "BLHeli_S (EFM8BB1 / EFM8BB2)"},
                        {"value": "Bluejay / BLHeli_S on EFM8BB51 (_X_ layout)"},
                        {"value": "Not sure"},
                    ],
                },
            },
        },
        {
            "title": "Preferred PWM frequency",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "48 kHz (Recommended for 1S/2S whoops & toothpicks)"},
                        {"value": "24 kHz (Recommended for 5-inch & heavy props)"},
                        {"value": "96 kHz"},
                        {"value": "All three (24 / 48 / 96 kHz)"},
                    ],
                },
            },
        },
        {
            "title": "Flight controller firmware you fly now (e.g. BetaFlight 3D Edition v0.3.1, Betaflight 4.5.1)",
            "question": {"required": False, "textQuestion": {}},
        },
        {
            "title": "Your 3D quad: frame, motors (size + kv), props, battery cells. Have you flown 3D on it already?",
            "question": {"required": True, "textQuestion": {"paragraph": True}},
        },
        {
            "title": "Will you fly the test and send logs? (the point of these builds is getting logs back)",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "Yes: the full 4-pack A/B test from the guide"},
                        {"value": "Yes: I'll fly it and send some logs"},
                        {"value": "Maybe: I mostly want to try it"},
                    ],
                },
            },
        },
        {
            "title": "Anything else we should know? (desync symptoms on stock Bluejay, questions, other boards)",
            "question": {"required": False, "textQuestion": {"paragraph": True}},
        },
    ]

    requests = [
        {
            "updateFormInfo": {
                "info": {
                    "title": "BlueJay3D: Request a Build for Your ESC / Board",
                    "description": description,
                },
                "updateMask": "title,description",
            }
        }
    ]
    for idx, q in enumerate(questions_spec):
        requests.append(
            {
                "createItem": {
                    "item": {
                        "title": q["title"],
                        "questionItem": {"question": q["question"]},
                    },
                    "location": {"index": idx},
                }
            }
        )

    forms_service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
    final_form = forms_service.forms().get(formId=form_id).execute()
    return {
        "formId": form_id,
        "responderUri": final_form.get("responderUri"),
        "editUri": f"https://docs.google.com/forms/d/{form_id}/edit",
    }


def create_log_upload_form(forms_service, drive_service, request_form_uri: str) -> dict:
    """
    Create BlueJay3D: Log & Feedback Upload by copying the BetaFlight 3D Edition Log Upload form
    (which preserves the two native Google Drive FileUploadQuestion items) and updating all fields.
    """
    copied = drive_service.files().copy(
        fileId=BF3D_LOG_FORM_ID,
        body={"name": "BlueJay3D - Log & Feedback Upload"},
    ).execute()
    form_id = copied["id"]

    existing = forms_service.forms().get(formId=form_id).execute()
    items = existing.get("items", [])

    description = (
        "Thanks for testing BlueJay3D! Upload your blackbox logs (.BBL) here, along with a few details "
        "about your ESC/drone and a short report. Every log helps prove (or disprove) the 9 backported "
        "AM32/ESCape32 3D commutation, braking, and fast-restart fixes across different 8-bit ESCs.\n\n"
        "Testing guide, firmware, presets, and configurator: "
        "https://github.com/BlindingBright/Drones/tree/bluejay3d/BlueJay3D\n\n"
        "File uploads need a Google sign-in (that's how Google Forms handles files). You can upload up to "
        f"10 logs at once. Need a build for a different ESC layout? Request one at {request_form_uri} "
        "or contact ZoeFPV (Discord link at zoefpv.com)."
    )

    # Map existing 15 items by index so we keep the 2 fileUploadQuestion items (indices 7 and 8)
    # and update their titles while replacing the text/choice/scale items cleanly.
    updates_by_index = {
        0: {
            "title": "Pilot name / callsign",
            "question": {"required": True, "textQuestion": {}},
        },
        1: {
            "title": "How can we contact you? (Discord name or email, optional)",
            "question": {"required": False, "textQuestion": {}},
        },
        2: {
            "title": "ESC Target & PWM Frequency (e.g. O_H_5 48kHz, Z_H_30 48kHz, G_H_30 24kHz, A_X_5 48kHz)",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "O_H_5 (48 kHz / 24 kHz / 96 kHz — BetaFPV / CrazyBee / Mobula AIO)"},
                        {"value": "Z_H_30 (48 kHz / 24 kHz — HGLRC Zeus / Flywoo Goku / GEPRC AIO)"},
                        {"value": "A_H_5 / S_H_50 / J_H_15 / M_H_5 (Whoop / Toothpick AIO)"},
                        {"value": "G_H_30 / Q_H_20 / H_H_30 (5-inch / 4-in-1 ESC)"},
                        {"value": "A_X_5 / B_X_30 (EFM8BB51 8-bit ESC)"},
                        {"value": "Another target from TARGETS.md (name it in the drone details)"},
                    ],
                },
            },
        },
        3: {
            "title": "Which ESC firmware did you fly?",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "BlueJay3D v0.22.0-3D (Block A stock-like vs Block B 3D optimized)"},
                        {"value": "BlueJay3D v0.22.0-3D (Block B 3D optimized only)"},
                        {"value": "Stock Bluejay v0.21.0 vs BlueJay3D v0.22.0-3D"},
                        {"value": "Stock BLHeli_S (for comparison)"},
                    ],
                },
            },
        },
        4: {
            "title": "Drone & FC details: AIO/ESC board name, frame, weight, motors (size + kv), props, battery (cells / mAh), Flight Controller firmware (e.g. BetaFlight 3D Edition v0.3.1)",
            "question": {"required": True, "textQuestion": {"paragraph": True}},
        },
        5: {
            "title": "BlueJay3D ESC settings (Brake Strength, Brake Speed, Min Duty, Rev Boost, Fast Restart, Fast Track, Glitch Filter, Startup Power, Timing)",
            "question": {"required": True, "textQuestion": {"paragraph": True}},
        },
        6: {
            "title": "Which BlueJay3D preset did you fly for Block B?",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "1S/2S 3D Whoop Preset (from the testing guide)"},
                        {"value": "3-4 inch Toothpick / Micro 3D Preset"},
                        {"value": "5-inch 3D Acro Preset"},
                        {"value": "My own custom settings in Bluejay3D Configurator"},
                    ],
                },
            },
        },
        # Index 7 & 8 are fileUploadQuestion items — only update their titles if desired, or leave intact!
        9: {
            "title": "Which settings was each log flown with? (e.g. pack1 + pack2 Block A / stock v0.21 behavior, pack3 + pack4 Block B / BlueJay3D full 3D features)",
            "question": {"required": True, "textQuestion": {"paragraph": True}},
        },
        10: {
            "title": "What did you fly in these logs? (tick all that apply)",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "CHECKBOX",
                    "options": [
                        {"value": "The 4-pack A/B test from the guide (flips with 1-2 s holds)"},
                        {"value": "Rapid tic-tocks (upright <-> inverted reversals)"},
                        {"value": "High-RPM full-stick reversals (active braking test)"},
                        {"value": "Zero-crossing hover / gentle center-stick transitions"},
                        {"value": "Punch-outs from reversals"},
                        {"value": "Inverted hover"},
                        {"value": "Freestyle 3D"},
                        {"value": "Bench test only (props off / bench_verify.py)"},
                    ],
                },
            },
        },
        11: {
            "title": "Compared with Block A (stock Bluejay v0.21 behavior), how did Block B (BlueJay3D) feel? (3 = no difference; skip if you only flew one mode)",
            "question": {
                "scaleQuestion": {
                    "low": 1,
                    "high": 5,
                    "lowLabel": "Much worse than stock Bluejay",
                    "highLabel": "Much better than stock Bluejay",
                }
            },
        },
        12: {
            "title": "Did you notice any of these? (tick all that apply)",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "CHECKBOX",
                    "options": [
                        {"value": "Clean, instant reversals with no desyncs"},
                        {"value": "Motor stall or desync (motor stopped, stuttered or squealed)"},
                        {"value": "Fast 1 ms recovery caught a desync mid-air without dropping an arm"},
                        {"value": "Deadband stutter or hesitation near stick center"},
                        {"value": "Drift or wobble after flips / reversals"},
                        {"value": "Hot motors or ESC"},
                        {"value": "Crash"},
                        {"value": "Nothing unusual"},
                        {"isOther": True},
                    ],
                },
            },
        },
        13: {
            "title": "Short report: how did it fly? Did BlueJay3D fix desyncs or center-stick stutters compared to stock Bluejay? (Mention which log/pack and roughly when.)",
            "question": {"required": True, "textQuestion": {"paragraph": True}},
        },
        14: {
            "title": "Can your logs and report be used in public analysis and upstream proposals to Bluejay / Betaflight?",
            "question": {
                "required": True,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [
                        {"value": "Yes, and you can credit me by name"},
                        {"value": "Yes, but keep me anonymous"},
                        {"value": "No, use them privately only"},
                    ],
                },
            },
        },
    }

    requests = [
        {
            "updateFormInfo": {
                "info": {
                    "title": "BlueJay3D: Log & Feedback Upload",
                    "description": description,
                },
                "updateMask": "title,description",
            }
        }
    ]

    for idx, spec in updates_by_index.items():
        if idx < len(items):
            item_id = items[idx]["itemId"]
            qid = items[idx].get("questionItem", {}).get("question", {}).get("questionId")
            q_body = dict(spec["question"])
            if qid:
                q_body["questionId"] = qid
            requests.append(
                {
                    "updateItem": {
                        "item": {
                            "itemId": item_id,
                            "title": spec["title"],
                            "questionItem": {"question": q_body},
                        },
                        "location": {"index": idx},
                        "updateMask": "title,questionItem.question",
                    }
                }
            )

    forms_service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
    final_form = forms_service.forms().get(formId=form_id).execute()
    return {
        "formId": form_id,
        "responderUri": final_form.get("responderUri"),
        "editUri": f"https://docs.google.com/forms/d/{form_id}/edit",
    }


def update_docs_with_urls(req_url: str, log_url: str):
    """Replace form URLs across BlueJay3D markdown docs and root README.md."""
    md_files = list(BJ3D_DIR.glob("*.md")) + [DRONES_ROOT / "README.md"]
    old_req = "https://forms.gle/1p93ZjiqDp1PLWA96"
    old_log = "https://forms.gle/Vfq3c2W7Lp5FE36t5"
    for md in md_files:
        if not md.exists():
            continue
        text = md.read_text()
        if md.name == "README.md" and md.parent == DRONES_ROOT:
            # Only replace inside the BlueJay3D section of root README.md
            if "## New: BlueJay3D" in text and "## New: BetaFlight 3D Edition" in text:
                parts = text.split("## New: BetaFlight 3D Edition", 1)
                parts[0] = parts[0].replace(old_req, req_url).replace(old_log, log_url)
                text = "## New: BetaFlight 3D Edition".join(parts)
        else:
            text = text.replace(old_req, req_url).replace(old_log, log_url)
        md.write_text(text)


def main():
    ap = argparse.ArgumentParser(description="Create BlueJay3D Google Forms")
    ap.add_argument("--timeout", type=int, default=0, help="OAuth browser timeout in seconds (0 = no timeout)")
    args = ap.parse_args()

    creds = get_credentials(timeout_sec=args.timeout)
    from googleapiclient.discovery import build

    forms_service = build("forms", "v1", credentials=creds, cache_discovery=False)
    drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)

    print("Creating Form 1: BlueJay3D Target Request Form...")
    req_form = create_target_request_form(forms_service)
    print(" -> Created:", req_form["responderUri"])

    print("Creating Form 2: BlueJay3D Log & Feedback Upload Form...")
    log_form = create_log_upload_form(forms_service, drive_service, req_form["responderUri"])
    print(" -> Created:", log_form["responderUri"])

    result = {
        "bluejay3d_requests": req_form,
        "bluejay3d_logs": log_form,
    }
    FORMS_CONFIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    FORMS_CONFIG_OUT.write_text(json.dumps(result, indent=2))
    update_docs_with_urls(req_form["responderUri"], log_form["responderUri"])
    print(f"Saved form metadata to {FORMS_CONFIG_OUT} and updated BlueJay3D markdown docs.")


if __name__ == "__main__":
    main()
