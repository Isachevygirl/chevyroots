"""Turso (libSQL) helper for Python pipelines.

Uses libsql-client-py if available, otherwise falls back to urllib + the
HTTP API. No hard dependency — pipelines degrade to file-only mode if
neither is available.

Environment variables:
    TURSO_DB_URL
    TURSO_AUTH_TOKEN
"""

import os
import json
import urllib.request
from typing import Optional, Any


class TursoClient:
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        self.url = url or os.environ.get("TURSO_DB_URL", "")
        self.token = token or os.environ.get("TURSO_AUTH_TOKEN", "")
        self.enabled = bool(self.url and self.token)
        if not self.enabled:
            print("[turso] TURSO_DB_URL or TURSO_AUTH_TOKEN not set; running in no-op mode")

    def execute(self, sql: str, args: list[Any] | None = None) -> dict:
        if not self.enabled:
            return {"rows": [], "rows_affected": 0}

        # Use the Turso HTTP v2 API for simple execution
        base = self.url.replace("libsql://", "https://").rstrip("/")
        endpoint = f"{base}/v2/pipeline"
        body = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": sql,
                        "args": [{"type": "text", "value": str(a) if a is not None else ""} for a in (args or [])],
                    },
                }
            ]
        }
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def log_pipeline_run(
        self,
        pipeline: str,
        status: str,
        items_processed: int = 0,
        items_new: int = 0,
        error: str = "",
        notes: str = "",
    ):
        if not self.enabled:
            return
        self.execute(
            """INSERT INTO pipeline_runs
               (pipeline, started_at, completed_at, status, items_processed, items_new, error, notes)
               VALUES (?, datetime('now'), datetime('now'), ?, ?, ?, ?, ?)""",
            [pipeline, status, items_processed, items_new, error, notes],
        )
