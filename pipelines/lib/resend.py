"""Thin Resend wrapper for pipeline alert emails."""

import os
import json
import urllib.request
from typing import Optional


RESEND_ENDPOINT = "https://api.resend.com/emails"


def send_alert(
    subject: str,
    body_text: str,
    *,
    to: str = "alerts@chevyroots.com",
    from_email: Optional[str] = None,
) -> bool:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print(f"[resend] no API key — would have sent: {subject}")
        return False

    sender = from_email or os.environ.get("RESEND_FROM_EMAIL") or "ChevyRoots Pipelines <alerts@chevyroots.com>"
    body = {
        "from": sender,
        "to": [to],
        "subject": subject,
        "text": body_text,
    }
    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            return True
    except Exception as e:
        print(f"[resend] send failed: {e}")
        return False
