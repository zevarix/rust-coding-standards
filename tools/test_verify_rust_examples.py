# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Contract tests for opt-in Rust example extraction (standard library only)."""
from __future__ import annotations

import unittest

from verify_rust_examples import extract_examples


class RustExampleParsing(unittest.TestCase):
    def test_compiles_only_tagged_preferred_examples(self) -> None:
        source = (
            "```rust\nbad Rust intentional example\n```\n\n"
            "<!-- rcs-example: test -->\n```rust\n"
            "#[test]\nfn sample() { assert!(true); }\n```\n"
        )
        examples, errors = extract_examples(source)
        self.assertFalse(errors)
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0].mode, "test")
        self.assertIn("assert!(true)", examples[0].code)

    def test_orphan_marker_rejected(self) -> None:
        _, errors = extract_examples(
            "<!-- rcs-example: compile -->\nNot a Rust fence\n"
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("standalone rust fence", errors[0])

    def test_empty_example_rejected(self) -> None:
        found, errors = extract_examples(
            "<!-- rcs-example: test -->\n```rust\n\n```\n"
        )
        self.assertEqual(found, [])
        self.assertEqual(len(errors), 1)

    def test_multiple_markers_do_not_swallow_each_other(self) -> None:
        text = (
            "<!-- rcs-example: compile -->\n```rust\npub fn a() {}\n```\n"
            "<!-- rcs-example: test -->\n```rust\n#[test] fn b() {}\n```\n"
        )
        found, errors = extract_examples(text)
        self.assertFalse(errors)
        self.assertEqual([x.mode for x in found], ["compile", "test"])


if __name__ == "__main__":
    unittest.main()
