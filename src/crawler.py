"""Crawler module for retrieving pages from quotes.toscrape.com."""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass
from typing import Callable, Iterable
from urllib.parse import urljoin

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
DEFAULT_TIMEOUT = 10.0
POLITENESS_WINDOW_SECONDS = 6.0


class CrawlError(RuntimeError):
    """Raised when a page cannot be fetched or parsed."""


@dataclass(frozen=True)
class CrawledPage:
    """Visible text and metadata extracted from one crawled page."""

    url: str
    title: str
    text: str
    next_url: str | None

    @property
    def word_count(self) -> int:
        return len(self.text.split())


class PoliteRequester:
    """Requests wrapper that enforces a delay before successive requests."""

    def __init__(
        self,
        session: requests.Session | None = None,
        delay_seconds: float = POLITENESS_WINDOW_SECONDS,
        sleep: Callable[[float], None] = time.sleep,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.session = session or requests.Session()
        self.delay_seconds = delay_seconds
        self.sleep = sleep
        self.timeout = timeout
        self._has_requested = False

    def get(self, url: str) -> str:
        if self._has_requested:
            self.sleep(self.delay_seconds)

        headers = {"User-Agent": "XJCO3011-CW2-SearchTool/1.0"}

        try:
            response = self.session.get(url, timeout=self.timeout, headers=headers)
            response.raise_for_status()
        except Exception as exc:  # requests and fake sessions expose varied errors.
            raise CrawlError(f"Failed to fetch {url}: {exc}") from exc

        self._has_requested = True
        return response.text


class QuoteCrawler:
    """Crawler for the coursework target website."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        delay_seconds: float = POLITENESS_WINDOW_SECONDS,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url
        self.requester = PoliteRequester(
            session=session,
            delay_seconds=delay_seconds,
            sleep=sleep,
            timeout=timeout,
        )

    def crawl(self) -> Iterable[CrawledPage]:
        """Yield pages by following the site's pagination links."""

        visited: set[str] = set()
        current_url: str | None = self.base_url

        while current_url and current_url not in visited:
            html = self.requester.get(current_url)
            page = self.parse_page(current_url, html)
            visited.add(current_url)
            yield page
            current_url = page.next_url

    def parse_page(self, url: str, html: str) -> CrawledPage:
        """Extract title, quote text, author names, tags, and next-page URL."""

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else url

        text_parts: list[str] = [title]
        for quote in soup.select(".quote"):
            quote_text = quote.select_one(".text")
            author = quote.select_one(".author")
            tags = [tag.get_text(" ", strip=True) for tag in quote.select(".tag")]

            if quote_text:
                text_parts.append(quote_text.get_text(" ", strip=True))
            if author:
                text_parts.append(author.get_text(" ", strip=True))
            text_parts.extend(tag for tag in tags if tag)

        next_link = soup.select_one("li.next a")
        next_url = urljoin(url, next_link["href"]) if next_link and next_link.has_attr("href") else None

        return CrawledPage(
            url=url,
            title=title,
            text=" ".join(part for part in text_parts if part),
            next_url=next_url,
        )
