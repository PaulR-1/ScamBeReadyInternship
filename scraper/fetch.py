from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests

from scraper.io_utils import load_json


class Fetcher:
    def __init__(self) -> None:
        settings = load_json("config/settings.json")
        self.delay = float(settings["request_delay_seconds"])
        self.timeout = float(settings["timeout_seconds"])
        self.user_agent = settings["user_agent"]
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self._robots: dict[str, RobotFileParser | None] = {}
        self._cache: dict[str, str | None] = {}

    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            robots_url = urljoin(origin, "/robots.txt")
            parser = RobotFileParser()
            try:
                response = self.session.get(robots_url, timeout=self.timeout)
                if response.status_code >= 400:
                    self._robots[origin] = None
                else:
                    parser.parse(response.text.splitlines())
                    self._robots[origin] = parser
            except requests.RequestException:
                self._robots[origin] = None
            time.sleep(self.delay)

        parser = self._robots[origin]
        if parser is None:
            return True
        return parser.can_fetch(self.user_agent, url)

    def get_text(self, url: str) -> str | None:
        if url in self._cache:
            return self._cache[url]
        if not self.allowed(url):
            self._cache[url] = None
            return None
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            time.sleep(self.delay)
            if response.status_code >= 400:
                self._cache[url] = None
                return None
            content_type = response.headers.get("Content-Type", "")
            if "html" not in content_type.lower() and not response.text.lstrip().startswith("<"):
                self._cache[url] = None
                return None
            self._cache[url] = response.text
            return response.text
        except requests.RequestException:
            self._cache[url] = None
            return None
