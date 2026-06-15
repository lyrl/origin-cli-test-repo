import pytest
from unittest.mock import patch, MagicMock
import requests

from scraper import fetch_html, parse_page, scrape, PageData, ScraperError


# ── fetch_html ────────────────────────────────────────────────────────────────

class TestFetchHtml:
    def test_returns_html_on_success(self):
        mock_resp = MagicMock()
        mock_resp.text = "<html><body>hello</body></html>"
        mock_resp.raise_for_status.return_value = None

        with patch("scraper.requests.get", return_value=mock_resp) as mock_get:
            result = fetch_html("https://example.com")

        mock_get.assert_called_once_with("https://example.com", timeout=10)
        assert result == "<html><body>hello</body></html>"

    def test_custom_timeout_is_forwarded(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.text = ""

        with patch("scraper.requests.get", return_value=mock_resp) as mock_get:
            fetch_html("https://example.com", timeout=5)

        mock_get.assert_called_once_with("https://example.com", timeout=5)

    def test_raises_scraper_error_on_connection_failure(self):
        with patch(
            "scraper.requests.get",
            side_effect=requests.exceptions.ConnectionError("refused"),
        ):
            with pytest.raises(ScraperError, match="Connection failed"):
                fetch_html("https://unreachable.example")

    def test_raises_scraper_error_on_timeout(self):
        with patch(
            "scraper.requests.get",
            side_effect=requests.exceptions.Timeout("timed out"),
        ):
            with pytest.raises(ScraperError, match="timed out"):
                fetch_html("https://slow.example")

    def test_raises_scraper_error_on_404(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        http_err = requests.exceptions.HTTPError(response=mock_resp)
        mock_resp.raise_for_status.side_effect = http_err

        with patch("scraper.requests.get", return_value=mock_resp):
            with pytest.raises(ScraperError, match="HTTP error"):
                fetch_html("https://example.com/missing")


# ── parse_page ────────────────────────────────────────────────────────────────

SAMPLE_HTML = """
<html>
  <head><title>Test Page</title></head>
  <body>
    <p>Hello world</p>
    <a href="https://example.com/page1">Page 1</a>
    <a href="https://example.com/page2">Page 2</a>
    <a href="/relative">Relative link</a>
  </body>
</html>
"""


class TestParsePage:
    def test_extracts_title(self):
        page = parse_page("https://example.com", SAMPLE_HTML)
        assert page.title == "Test Page"

    def test_extracts_absolute_links_only(self):
        page = parse_page("https://example.com", SAMPLE_HTML)
        assert page.links == [
            "https://example.com/page1",
            "https://example.com/page2",
        ]

    def test_relative_links_excluded(self):
        page = parse_page("https://example.com", SAMPLE_HTML)
        assert "/relative" not in page.links

    def test_extracts_text(self):
        page = parse_page("https://example.com", SAMPLE_HTML)
        assert "Hello world" in page.text

    def test_url_stored_on_page(self):
        page = parse_page("https://example.com", SAMPLE_HTML)
        assert page.url == "https://example.com"

    def test_missing_title_defaults_to_empty_string(self):
        html = "<html><body><p>No title</p></body></html>"
        page = parse_page("https://example.com", html)
        assert page.title == ""

    def test_page_with_no_links(self):
        html = "<html><body><p>No links here</p></body></html>"
        page = parse_page("https://example.com", html)
        assert page.links == []


# ── scrape (integration of fetch + parse) ─────────────────────────────────────

class TestScrape:
    def test_scrape_returns_page_data(self):
        mock_resp = MagicMock()
        mock_resp.text = SAMPLE_HTML
        mock_resp.raise_for_status.return_value = None

        with patch("scraper.requests.get", return_value=mock_resp):
            page = scrape("https://example.com")

        assert isinstance(page, PageData)
        assert page.title == "Test Page"
        assert len(page.links) == 2

    def test_scrape_propagates_scraper_error(self):
        with patch(
            "scraper.requests.get",
            side_effect=requests.exceptions.ConnectionError("down"),
        ):
            with pytest.raises(ScraperError):
                scrape("https://down.example")
