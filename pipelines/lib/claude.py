"""Claude API wrapper for pipeline summarization and drafting.

Requires ANTHROPIC_API_KEY in the environment.
"""

import os
import json
import urllib.request
from typing import Optional


ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # Fast + cheap for summaries
DRAFTING_MODEL = "claude-sonnet-4-6"  # For article drafting and forum synthesis


def call_claude(
    prompt: str,
    *,
    system: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    temperature: float = 0.5,
) -> str:
    """Call the Anthropic Messages API and return the text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set. See .env.example.")

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    req = urllib.request.Request(
        ANTHROPIC_ENDPOINT,
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    content = data.get("content", [])
    if not content:
        return ""
    return content[0].get("text", "")


def summarize_news(title: str, body: str) -> str:
    """Summarize a news article into 100-150 words for the news feed."""
    prompt = f"""Summarize this Chevrolet-related news article in 100–150 words. Keep
it factual, neutral, and specific. Include model, year, and dollar figures if
they are mentioned. Do not editorialize. Do not use "I" or "we". Plain text only.

Title: {title}

Body:
{body}
"""
    return call_claude(prompt, max_tokens=400)


def draft_recall_post(recall_data: dict) -> str:
    """Draft a short post about a new NHTSA recall in Crystal's voice."""
    prompt = f"""Write a short (150–250 word) post about this Chevrolet recall,
in Crystal's voice — honest, direct, helpful to owners. Explain what the
recall covers, which vehicles are affected, what owners should do, and
whether this is the kind of thing to take seriously.

Voice guidelines:
- Crystal-owned ZR2 driver, not a dealer mouthpiece
- Direct and practical, no fluff
- No "click here to learn more" filler
- Link to the NHTSA page at the end: {recall_data.get('nhtsa_url', '')}

Recall data:
{json.dumps(recall_data, indent=2)}
"""
    return call_claude(prompt, max_tokens=600, model=DRAFTING_MODEL)
