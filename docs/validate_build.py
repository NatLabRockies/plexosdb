"""Validate built documentation routes, local links, and legacy redirects."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "_build"
BASE = "/plexosdb/"


class Page(HTMLParser):
    """Collect links, fragment IDs, and redirect-script references."""

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.scripts: list[str] = []
        self.feed(path.read_text())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect IDs and links from one HTML start tag."""
        attributes = dict(attrs)
        if identifier := attributes.get("id"):
            self.ids.add(identifier)
        if tag == "a" and (href := attributes.get("href")):
            self.links.append(href)
        if tag == "script" and (src := attributes.get("src")):
            self.scripts.append(src)


def page_for(target: str) -> Path:
    url = urlsplit(target)
    assert url.path.startswith(BASE), target
    destination = BUILD / unquote(url.path.removeprefix(BASE))
    if destination.is_dir():
        destination /= "index.html"
    return destination


def validate() -> None:
    pages = {path: Page(path) for path in BUILD.rglob("*.html")}
    assert pages, "Build the site before validating links"
    checked = 0
    for origin, page in pages.items():
        for target in page.links:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path.startswith(BASE):
                continue
            destination = page_for(target)
            assert destination.is_file(), (origin, target)
            if url.fragment:
                assert unquote(url.fragment) in pages[destination].ids, (origin, target)
            checked += 1

    fragments = json.loads((ROOT / "public/api-fragments.json").read_text())
    for target in fragments.values():
        destination = page_for(target)
        assert destination.is_file(), target
        fragment = urlsplit(target).fragment
        if fragment:
            assert unquote(fragment) in pages[destination].ids, target

    assert (BUILD / "index.html").is_file()
    assert (BUILD / "reference/python-api/index.html").is_file()
    assert (BUILD / "reference/python-api/plexosdb/index.html").is_file()
    legacy_pages = [path for path in BUILD.rglob("*.html") if "page moved" in path.read_text().lower()]
    assert legacy_pages
    for path in legacy_pages:
        page = pages[path]
        assert "/plexosdb/legacy-redirect.js" in page.scripts, path
        assert page.links, path
    print(f"Checked {len(pages)} HTML pages, {checked} internal links, and {len(fragments)} API bookmarks")


if __name__ == "__main__":
    validate()
