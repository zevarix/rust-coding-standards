#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Verify generated search metadata and agent-discovery files in the built site.

This checks rendered output rather than assuming a configuration or plugin worked.
It does not measure ranking, indexing, crawler behavior or Search Console state.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

from verify_standards import html_element_ids

SITE_URL = "https://rcs.zevarix.com/"
CHECKED_PAGES = (
    "",
    "standards/",
    "topics/",
    "ai-rust-code-quality/",
    "review-guide/",
    "rules/performance/",
    "rules/testing/",
    "performance/optimization/",
    "verification/assurance/",
)


class PageHead(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.h1_count = 0
        self.social: dict[str, str] = {}
        self.edit_action = False
        self.view_action = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = dict(attrs)
        if tag == "meta" and fields.get("property") in ("og:title", "og:image", "twitter:card"):
            self.social[fields["property"]] = fields.get("content") or ""
        if tag == "a":
            href = fields.get("href") or ""
            self.edit_action |= href.startswith(
                "https://github.com/zevarix/rust-coding-standards/edit/main/docs/"
            )
            self.view_action |= href.startswith(
                "https://github.com/zevarix/rust-coding-standards/raw/main/docs/"
            )
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and fields.get("name", "").lower() == "description":
            self.descriptions.append(fields.get("content") or "")
        elif tag == "link" and fields.get("rel") == "canonical":
            self.canonicals.append(fields.get("href") or "")
        elif tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def check_site(site: Path) -> list[str]:
    problems: list[str] = []
    descriptions: set[str] = set()

    for suffix in CHECKED_PAGES:
        file = site / suffix / "index.html"
        if not file.is_file():
            problems.append(f"Missing rendered page: {file}")

    for file in sorted(site.rglob("index.html")):
        parent = file.relative_to(site).parent
        suffix = "" if parent == Path(".") else parent.as_posix() + "/"
        head = PageHead()
        head.feed(file.read_text(encoding="utf-8"))
        if not head.title.strip() or head.title.startswith("Home - "):
            problems.append(f"Unhelpful or missing page title: {suffix or '/'}")
        if len(head.descriptions) != 1 or not head.descriptions[0].strip():
            problems.append(f"Missing or unreasonable page description: {suffix or '/'}")
        else:
            if head.descriptions[0] in descriptions:
                problems.append(f"Duplicate page description: {suffix or '/'}")
            descriptions.add(head.descriptions[0])
        if head.canonicals != [SITE_URL + suffix]:
            problems.append(f"Incorrect canonical URL: {suffix or '/'}")
        if head.h1_count != 1:
            problems.append(f"Expected one page H1: {suffix or '/'}")
        for name in ("og:title", "og:image", "twitter:card"):
            if not head.social.get(name):
                problems.append(f"Missing social metadata {name}: {suffix or '/'}")
        image = head.social.get("og:image", "")
        if image and (
            not image.startswith(SITE_URL)
            or not (site / urlparse(image).path.lstrip("/")).is_file()
        ):
            problems.append(f"Missing generated social-card image: {suffix or '/'}")
        if not head.edit_action or not head.view_action:
            problems.append(f"Missing current main source/edit actions: {suffix or '/'}")
        if suffix == "topics/":
            ids = html_element_ids(file.read_text(encoding="utf-8"))
            for tag in ("performance", "testing", "safety", "ai-assisted-development"):
                if f"tag:{tag}" not in ids:
                    problems.append(f"Topics index missing tag group {tag}")
    search = site / "search.json"
    if not search.is_file() or "AI-assisted Development" not in search.read_text(encoding="utf-8"):
        problems.append("Search index missing tagged AI-assisted Development content")

    robots = site / "robots.txt"
    if not robots.is_file() or "Sitemap: https://rcs.zevarix.com/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        problems.append("Missing robots.txt sitemap discovery")
    sitemap = site / "sitemap.xml"
    if not sitemap.is_file():
        problems.append("Missing generated sitemap.xml")
    else:
        try:
            root = ElementTree.parse(sitemap).getroot()
            urls = {node.text for node in root.iter() if node.tag.endswith("}loc") or node.tag == "loc"}
            for file in sorted(site.rglob("index.html")):
                parent = file.relative_to(site).parent
                suffix = "" if parent == Path(".") else parent.as_posix() + "/"
                if SITE_URL + suffix not in urls:
                    problems.append(f"Page absent from sitemap: {suffix or '/'}")
        except ElementTree.ParseError as exc:
            problems.append(f"Invalid sitemap XML: {exc}")

    public_keys = sorted(site.glob("indexnow-*.txt"))
    if len(public_keys) != 1:
        problems.append("Expected exactly one public IndexNow verification file")
    else:
        marker = public_keys[0]
        if marker.read_text(encoding="utf-8") != marker.stem:
            problems.append("IndexNow verification file must contain its public key exactly")

    llms = site / "llms.txt"
    full = site / "llms-full.txt"
    if not llms.is_file() or not full.is_file():
        problems.append("Missing Zensical-generated llms.txt or llms-full.txt")
        return problems

    index = llms.read_text(encoding="utf-8")
    complete = full.read_text(encoding="utf-8")
    if "AI-generated Rust" not in index or "ai-rust-code-quality/index.md" not in index:
        problems.append("AI Rust quality guide absent from llms.txt")
    if not all(phrase in complete for phrase in ("RCS-PERF-001", "RCS-TEST-004", "Anti AI Slop Rust")):
        problems.append("llms-full.txt does not contain expected current standards and guide")
    if len(complete) <= len(index):
        problems.append("llms-full.txt is not expanded beyond its index")

    exports = re.findall(r"<(https://rcs\.zevarix\.com/[^>]+\.md)>", index)
    if not exports:
        problems.append("No Markdown page exports found in llms.txt")
    for url in exports:
        relative = urlparse(url).path.lstrip("/")
        if not (site / relative).is_file():
            problems.append(f"Missing linked Markdown export: {relative}")
    return problems


if __name__ == "__main__":
    site_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "site"
    issues = check_site(site_dir.resolve())
    for issue in issues:
        print("FAIL:", issue)
    if issues:
        raise SystemExit(1)
    print("PASS: all rendered page titles, unique descriptions, canonicals, H1s, "
          "social cards, source actions and sitemap; topic tags and AI exports verified")
