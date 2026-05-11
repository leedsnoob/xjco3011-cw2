"""Reusable fixtures for crawler, indexer, search, and CLI tests."""

from __future__ import annotations

from dataclasses import dataclass


PAGE_ONE_HTML = """
<!doctype html>
<html>
  <head><title>Quotes to Scrape</title></head>
  <body>
    <div class="quote">
      <span class="text">“The world as we have created it is a process of our thinking.”</span>
      <small class="author">Albert Einstein</small>
      <a class="tag">change</a>
      <a class="tag">world</a>
    </div>
    <div class="quote">
      <span class="text">“It is our choices that show what we truly are.”</span>
      <small class="author">J.K. Rowling</small>
      <a class="tag">choices</a>
    </div>
    <nav>
      <ul class="pager">
        <li class="next"><a href="/page/2/">Next <span aria-hidden="true">&rarr;</span></a></li>
      </ul>
    </nav>
  </body>
</html>
"""


PAGE_TWO_HTML = """
<!doctype html>
<html>
  <head><title>Quotes to Scrape - Page 2</title></head>
  <body>
    <div class="quote">
      <span class="text">“Good friends, good books, and a sleepy conscience: this is the ideal life.”</span>
      <small class="author">Mark Twain</small>
      <a class="tag">friends</a>
      <a class="tag">books</a>
    </div>
  </body>
</html>
"""


@dataclass
class FakeResponse:
    """Small response object matching the requests API used by the crawler."""

    text: str
    status_code: int = 200
    url: str = "https://quotes.toscrape.com/"

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    """Deterministic requests-like session for crawler tests."""

    def __init__(self, pages: dict[str, str | FakeResponse]):
        self.pages = pages
        self.requested_urls: list[str] = []

    def get(self, url: str, timeout: float, headers: dict[str, str]) -> FakeResponse:
        self.requested_urls.append(url)
        response = self.pages[url]
        if isinstance(response, FakeResponse):
            response.url = url
            return response
        return FakeResponse(text=response, url=url)
