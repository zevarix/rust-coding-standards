#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Build the read-only RCS MCP catalog from the canonical Markdown rulebook.

Deterministic output; no network, private source, credentials, or timestamps.
The embedded revision is the exact Git commit containing the inspected bytes.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

# Reuse the repository's authoritative heading/index grammar.
from verify_standards import INDEX_LINK, RULE_HEADING

SITE = "https://rcs.zevarix.com/"
SOURCE = "https://github.com/zevarix/rust-coding-standards/blob"
GUIDES: dict[str, str] = {
    "adoption": "adoption.md",
    "review-guide": "review-guide.md",
    "verification": "verification/assurance.md",
    "anti-ai-slop": "ai-rust-code-quality.md",
    "measurement": "performance/measurement.md",
    "profiling": "performance/profiling.md",
    "optimization": "performance/optimization.md",
}

ROW = re.compile(
    r"^\|\s*\[(RCS-[A-Z]+-\d{3})\]\((rules/[a-z0-9-]+\.md#[a-z0-9-]+)\)\s*"
    r"\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|\n]+)\|", re.MULTILINE
)


def source_revision(root: Path) -> str:
    value = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("Git did not return an exact source commit")
    return value


def public_doc(docs: Path, relative: str) -> str:
    path = (docs / relative).resolve()
    if not path.is_relative_to(docs.resolve()) or not path.is_file() or path.is_symlink():
        raise ValueError(f"Noncanonical or missing public RCS document: {relative}")
    return path.read_text(encoding="utf-8")


def document_links(relative: str, revision: str, anchor: str = "") -> tuple[str, str]:
    slug = relative.removesuffix(".md") + "/"
    suffix = ("#" + quote(anchor, safe="-")) if anchor else ""
    return (
        SITE + slug + suffix,
        f"{SOURCE}/{revision}/docs/{relative}{suffix}",
    )


def build_catalog(root: Path, revision: str | None = None) -> dict[str, object]:
    root = root.resolve()
    docs = root / "docs"
    revision = revision or source_revision(root)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Catalog revision must be a complete commit SHA")

    standards = public_doc(docs, "standards.md")
    links = INDEX_LINK.findall(standards)
    rows = list(ROW.finditer(standards))
    if not rows or len(rows) != len(links):
        raise ValueError("Standards index rows must be parsable without loss")
    row_refs = [(m.group(1), m.group(2)) for m in rows]
    if row_refs != links:
        raise ValueError("Standards row ordering/links differ from the authoritative index")
    if len({rule_id for rule_id, _ in links}) != len(links):
        raise ValueError("Duplicate standards rule ID")

    pages = sorted((docs / "rules").glob("*.md"))
    discovered: dict[str, dict[str, str]] = {}
    for page in pages:
        relative = page.relative_to(docs).as_posix()
        data = public_doc(docs, relative)
        matches = list(RULE_HEADING.finditer(data))
        if not matches:
            raise ValueError(f"Rule page has no indexed headings: {relative}")
        for i, match in enumerate(matches):
            rule_id, anchor = match.groups()
            if rule_id in discovered:
                raise ValueError(f"Duplicate rule heading: {rule_id}")
            heading = data[match.start():match.end()].strip()
            title = heading.split(" — ", 1)
            if len(title) != 2:
                raise ValueError(f"Missing rule title: {rule_id}")
            clean_title = title[1].rsplit(" {#", 1)[0].strip()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
            body = data[match.start():content_end].strip()
            discovered[rule_id] = {
                "file": relative,
                "anchor": anchor,
                "title": clean_title,
                "markdown": body,
            }

    rules: list[dict[str, object]] = []
    for row in rows:
        rule_id, href = row.group(1, 2)
        data = discovered.get(rule_id)
        if not data:
            raise ValueError(f"Index row missing rule heading: {rule_id}")
        expected_href = f"{data['file']}#{data['anchor']}"
        if href != expected_href:
            raise ValueError(f"Index href mismatch for {rule_id}: {href} != {expected_href}")
        published, exact_source = document_links(data["file"], revision, data["anchor"])
        rules.append({
            "id": rule_id,
            "title": data["title"],
            "level": row.group(3).strip(),
            "enforcement": row.group(4).strip(),
            "summary": row.group(5).strip(),
            "markdown": data["markdown"],
            "url": published,
            "source_url": exact_source,
        })

    if set(discovered) != {r["id"] for r in rules}:
        raise ValueError("An RCS heading is missing from the canonical index")

    guides: list[dict[str, object]] = []
    for key, relative in GUIDES.items():
        text = public_doc(docs, relative)
        # Do not expose Zensical frontmatter as if it were part of the guidance.
        if text.startswith("---\n"):
            parts = text.split("\n---\n", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid guide frontmatter: {relative}")
            text = parts[1].lstrip()
        heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if not heading:
            raise ValueError(f"Guide has no H1: {relative}")
        published, exact_source = document_links(relative, revision)
        guides.append({
            "id": key,
            "title": heading.group(1),
            "markdown": text.strip(),
            "url": published,
            "source_url": exact_source,
        })

    return {
        "schema": "rcs-mcp-catalog/v1",
        "revision": revision,
        "index_url": SITE + "standards/",
        "rules": rules,
        "guides": guides,
    }


def write_catalog(root: Path, output: Path, revision: str | None = None) -> None:
    catalog = build_catalog(root, revision)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    output.write_text(data, encoding="utf-8", newline="\n")
    print(f"PASS: {len(catalog['rules'])} canonical RCS rules and "
          f"{len(catalog['guides'])} guides indexed from {catalog['revision']}")
    print(f"CATALOG={output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--revision", type=str)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "mcp" / "rcs" / "src" / "generated" / "catalog.json").resolve()
    write_catalog(root, output, args.revision)
