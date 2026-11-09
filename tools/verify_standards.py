#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Validate the single-source RCS Markdown rule index and local links.

Standard library only; optional --site verifies generated Zensical anchors.
No fixed number of rules, page length quota, or mandatory third-party linter.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

RULE_HEADING = re.compile(
    r"^## (RCS-[A-Z]+-[0-9]{3})\b[^\n]*\{#(rcs-[a-z]+-[0-9]{3}--[a-z0-9-]+)\}\s*$",
    re.MULTILINE,
)
INDEX_LINK = re.compile(
    r"^\| \[(RCS-[A-Z]+-[0-9]{3})\]\(([^)\n]+)\)",
    re.MULTILINE,
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")


def validate(root: Path, verify_site: bool) -> list[str]:
    errors: list[str] = []
    docs = root / "docs"
    rules = docs / "rules"
    index = docs / "standards.md"
    config = root / "mkdocs.yml"

    if not index.is_file() or not rules.is_dir() or not config.is_file():
        return ["Missing docs/standards.md, docs/rules/ or mkdocs.yml"]

    headings: dict[str, tuple[Path, str]] = {}
    rule_pages = sorted(rules.glob("*.md"))
    for page in rule_pages:
        source = page.read_text(encoding="utf-8")
        found = RULE_HEADING.findall(source)
        if not found:
            errors.append(f"{page.relative_to(root)}: no indexed RCS rule heading")
        for rule_id, anchor in found:
            if rule_id in headings:
                errors.append(f"Duplicate {rule_id}: {headings[rule_id][0]} and {page}")
            headings[rule_id] = (page.resolve(), anchor)
            if anchor.split("--", 1)[0] != rule_id.lower():
                errors.append(f"{rule_id}: heading anchor does not match the rule ID")

    source_index = index.read_text(encoding="utf-8")
    seen: set[str] = set()
    for rule_id, href in INDEX_LINK.findall(source_index):
        if rule_id in seen:
            errors.append(f"Duplicate standards index entry: {rule_id}")
            continue
        seen.add(rule_id)
        if rule_id not in headings:
            errors.append(f"Indexed rule has no matching heading: {rule_id}")
            continue
        if "#" not in href:
            errors.append(f"{rule_id}: index must deep-link to the rule anchor")
            continue
        target, anchor = href.split("#", 1)
        actual_page, actual_anchor = headings[rule_id]
        if (docs / target).resolve() != actual_page or anchor != actual_anchor:
            errors.append(f"{rule_id}: index target {href} differs from its rule heading")
    for rule_id in headings.keys() - seen:
        errors.append(f"Rule heading missing from standards index: {rule_id}")

    rule_paths = {p for p, _ in headings.values()}
    source_files = sorted(docs.rglob("*.md"))
    source_files += sorted((root / "skills").rglob("*.md"))
    for page in source_files:
        content = page.read_text(encoding="utf-8")
        if "ZR-" in content or "zr-" in content:
            errors.append(f"{page.relative_to(root)}: retired ZR- identifier remains")
        for href in MARKDOWN_LINK.findall(content):
            parsed = urlsplit(href.strip())
            if parsed.scheme or parsed.netloc or href.startswith("#"):
                continue
            if not parsed.path:
                continue
            path = (page.parent / unquote(parsed.path)).resolve()
            if not path.is_file():
                errors.append(f"{page.relative_to(root)}: broken relative link {href}")
            elif parsed.fragment and path in rule_paths:
                anchors = {a for p, a in headings.values() if p == path}
                if unquote(parsed.fragment) not in anchors:
                    errors.append(f"{page.relative_to(root)}: unknown rule anchor in {href}")

    nav = config.read_text(encoding="utf-8")
    for page in rule_pages:
        if f"rules/{page.name}" not in nav:
            errors.append(f"{page.relative_to(root)}: not listed in navigation")
    if "review-guide.md" not in nav:
        errors.append("Reviewer guide not listed in navigation")
    css = root / "docs/stylesheets/forge.css"
    if css.is_file() and 'h2[id^="rcs-"]' not in css.read_text(encoding="utf-8"):
        errors.append("Theme must style current RCS rule headings")

    if verify_site:
        site = root / "site"
        for rule_id, (page, anchor) in headings.items():
            built = site / page.relative_to(docs).with_suffix("") / "index.html"
            if not built.is_file():
                errors.append(f"{rule_id}: no generated HTML {built}")
            elif f'id="{anchor}"' not in built.read_text(encoding="utf-8"):
                errors.append(f"{rule_id}: missing generated HTML anchor {anchor}")
        if not (site / "search.json").is_file():
            errors.append("Generated search index missing")

    if not errors:
        print(f"PASS: {len(headings)} indexed RCS rules across {len(rule_pages)} pages; "
              f"links, navigation and anchors valid"
              + ("; generated HTML/search verified" if verify_site else ""))
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="Root of the documentation repository")
    parser.add_argument("--site", action="store_true",
                        help="Also verify generated HTML from a prior Zensical build")
    opts = parser.parse_args()
    problems = validate(opts.root.resolve(), opts.site)
    for error in problems:
        print("FAIL:", error)
    raise SystemExit(1 if problems else 0)
