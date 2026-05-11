"""Tests for crawler behavior."""

from __future__ import annotations

import pytest

from tests.fixtures import FakeResponse, FakeSession, PAGE_ONE_HTML, PAGE_TWO_HTML


def test_crawler_follows_pagination_and_extracts_quote_text() -> None:
    from src.crawler import QuoteCrawler

    session = FakeSession(
        {
            "https://quotes.toscrape.com/": PAGE_ONE_HTML,
            "https://quotes.toscrape.com/page/2/": PAGE_TWO_HTML,
        }
    )
    sleeps: list[float] = []

    crawler = QuoteCrawler(session=session, sleep=sleeps.append)
    pages = list(crawler.crawl())

    assert session.requested_urls == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert sleeps == [6.0]
    assert [page.url for page in pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert "Albert Einstein" in pages[0].text
    assert "Good friends" in pages[1].text
    assert pages[0].next_url == "https://quotes.toscrape.com/page/2/"


def test_parse_page_keeps_title_quotes_authors_and_tags() -> None:
    from src.crawler import QuoteCrawler

    page = QuoteCrawler().parse_page("https://quotes.toscrape.com/", PAGE_ONE_HTML)

    assert page.title == "Quotes to Scrape"
    assert "process of our thinking" in page.text
    assert "J.K. Rowling" in page.text
    assert "choices" in page.text
    assert page.word_count > 20


def test_crawler_wraps_request_failures_in_crawl_error() -> None:
    from src.crawler import CrawlError, QuoteCrawler

    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(
                text="server error",
                status_code=500,
            )
        }
    )

    crawler = QuoteCrawler(session=session, sleep=lambda seconds: None)

    with pytest.raises(CrawlError, match="Failed to fetch"):
        list(crawler.crawl())
