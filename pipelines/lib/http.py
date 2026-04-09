"""Polite HTTP client with robots.txt compliance, rate limiting, and
an identified User-Agent. Used by every scraper in the pipelines directory.

Usage:
    from lib.http import PoliteClient
    client = PoliteClient(rate_limit_seconds=5)
    response = client.get("https://example.com/some-page")
"""

import time
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse
from typing import Optional


DEFAULT_USER_AGENT = (
    "ChevyRootsBot/1.0 (+https://chevyroots.com/bot; contact hello@chevyroots.com)"
)


class PoliteClient:
    """HTTP client that respects robots.txt, rate-limits per domain, and
    identifies itself. Used by every scraper."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        rate_limit_seconds: float = 5.0,
        timeout: float = 30.0,
        respect_robots: bool = True,
    ):
        self.user_agent = user_agent
        self.rate_limit_seconds = rate_limit_seconds
        self.timeout = timeout
        self.respect_robots = respect_robots
        self._last_request_at: dict[str, float] = {}
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _get_robots_parser(self, url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin in self._robots_cache:
            return self._robots_cache[origin]
        parser = urllib.robotparser.RobotFileParser()
        robots_url = f"{origin}/robots.txt"
        try:
            parser.set_url(robots_url)
            parser.read()
            self._robots_cache[origin] = parser
            return parser
        except Exception:
            # Fail open on robots.txt read errors, but log it
            print(f"[http] Could not fetch robots.txt from {robots_url} — proceeding with caution")
            return None

    def can_fetch(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parser = self._get_robots_parser(url)
        if parser is None:
            return True
        return parser.can_fetch(self.user_agent, url)

    def _wait_for_rate_limit(self, domain: str):
        now = time.time()
        last = self._last_request_at.get(domain, 0.0)
        elapsed = now - last
        if elapsed < self.rate_limit_seconds:
            sleep_for = self.rate_limit_seconds - elapsed
            time.sleep(sleep_for)
        self._last_request_at[domain] = time.time()

    def get(self, url: str, *, extra_headers: Optional[dict] = None) -> bytes:
        if not self.can_fetch(url):
            raise PermissionError(f"robots.txt disallows {url} for {self.user_agent}")
        domain = urlparse(url).netloc
        self._wait_for_rate_limit(domain)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml,application/rss+xml;q=0.9,*/*;q=0.8",
                **(extra_headers or {}),
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read()

    def get_text(self, url: str) -> str:
        return self.get(url).decode("utf-8", errors="replace")
