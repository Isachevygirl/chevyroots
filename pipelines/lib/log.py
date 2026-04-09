"""Structured logging that writes to both stdout and Turso."""

import json
import sys
import time
from typing import Any


def log(event: str, **fields: Any):
    """Print a JSON log line and return the record for composition."""
    record = {"ts": time.time(), "event": event, **fields}
    print(json.dumps(record, default=str), file=sys.stderr)
    return record
