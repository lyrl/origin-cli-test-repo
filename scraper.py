import argparse
import json
import sys

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PageData:
    url: str
    title: str
    links: list[str] = field(default_factory=list)
    text: str = ""


class ScraperError(Exception):
    pass


def fetch_html(url: str, timeout: int = 10) -> str:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectionError as e:
        raise ScraperError(f"Connection failed: {e}") from e
    except requests.exceptions.Timeout as e:
        raise ScraperError(f"Request timed out: {e}") from e
    except requests.exceptions.HTTPError as e:
        raise ScraperError(f"HTTP error {e.response.status_code}: {e}") from e


def parse_page(url: str, html: str) -> PageData:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith("http")
    ]

    text = soup.get_text(separator=" ", strip=True)

    return PageData(url=url, title=title, links=links, text=text)


def scrape(url: str, timeout: int = 10) -> PageData:
    html = fetch_html(url, timeout=timeout)
    return parse_page(url, html)


def main():
    parser = argparse.ArgumentParser(description="Scrape a webpage")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    parser.add_argument("--links", action="store_true", help="Print extracted links")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    try:
        page = scrape(args.url, timeout=args.timeout)
    except ScraperError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"url": page.url, "title": page.title, "links": page.links, "text": page.text}, ensure_ascii=False, indent=2))
    elif args.links:
        for link in page.links:
            print(link)
    else:
        print(f"Title: {page.title}")
        print(f"Links: {len(page.links)}")
        print(f"Text:  {page.text[:200]}...")


if __name__ == "__main__":
    print(f"Title: hhhhhhhhhhhhhhhhhh")
    main()
