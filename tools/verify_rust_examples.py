#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Compile explicitly marked Rust examples from the RCS rulebook.

Only immediately adjacent <!-- rcs-example: test|compile --> fenced Rust
blocks are executable contracts. Intentional anti-examples, pseudocode,
and illustrative fragments remain documentation, not executable tests.
Uses only Python's standard library and the installed rustc.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

MARKER = re.compile(r"(?m)^<!-- rcs-example: ([a-z-]+) -->[ \t]*$")
TAGGED = re.compile(
    r"(?ms)^<!-- rcs-example: (?P<mode>test|compile) -->[ \t]*\n"
    r"(?:[ \t]*\n)*```rust[ \t]*\n(?P<code>.*?)\n```[ \t]*$"
)


@dataclass(frozen=True)
class Example:
    mode: str
    code: str
    line: int


def extract_examples(markdown: str) -> tuple[list[Example], list[str]]:
    """Require each marker to own an immediately following fenced Rust block."""
    examples: list[Example] = []
    errors: list[str] = []
    all_markers = list(MARKER.finditer(markdown))
    matched = list(TAGGED.finditer(markdown))

    if len(all_markers) != len(matched):
        found = {m.start() for m in matched}
        for mark in all_markers:
            if mark.start() not in found:
                errors.append(
                    f"line {markdown.count(chr(10), 0, mark.start()) + 1}: "
                    "marker must be followed by a standalone rust fence"
                )
    for match in matched:
        line = markdown.count("\n", 0, match.start()) + 1
        if not match.group("code").strip():
            errors.append(f"line {line}: executable Rust example is empty")
        else:
            examples.append(Example(match.group("mode"), match.group("code"), line))
    return examples, errors


def run(command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    return result.returncode == 0, (result.stdout + "\n" + result.stderr).strip()


def validate(root: Path, rustc: str) -> int:
    pages = sorted((root / "docs" / "rules").glob("*.md"))
    if not pages:
        print("FAIL: no Rust rule pages found")
        return 1

    found = 0
    failures = []
    with tempfile.TemporaryDirectory(prefix="rcs-examples-") as temporary:
        work = Path(temporary)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            examples, errors = extract_examples(text)
            failures.extend(
                f"{page.relative_to(root)}: {problem}" for problem in errors
            )
            for example in examples:
                found += 1
                label = f"{page.relative_to(root)}:{example.line}"
                source = work / f"rcs_example_{found}.rs"
                source.write_text(example.code + "\n", encoding="utf-8")
                dest = work / f"rcs_example_{found}"
                if sys.platform == "win32":
                    dest = dest.with_suffix(".exe")
                command = [
                    rustc,
                    "--edition=2024",
                    "--crate-name", f"rcs_example_{found}",
                    "--test" if example.mode == "test" else "--crate-type=lib",
                    str(source), "-o", str(dest), "-D", "warnings",
                ]
                compiled, details = run(command)
                if not compiled:
                    failures.append(f"{label} ({example.mode}) compile FAIL:\n{details}")
                    continue
                if example.mode == "test":
                    passed, details = run([str(dest), "--nocapture"])
                    if not passed:
                        failures.append(f"{label} run FAIL:\n{details}")
                        continue
                print(f"PASS: {label} ({example.mode})")
    if found == 0:
        failures.append("No marked Rust examples: an empty check is not a PASS")
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"PASS: {found} explicitly marked Rust examples compiled"
          " and all marked tests ran")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--rustc", default="rustc")
    options = parser.parse_args()
    raise SystemExit(validate(options.root.resolve(), options.rustc))
