#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Source-faithful and negative-path checks for public RCS MCP indexing."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_rcs_mcp_index import GUIDES, build_catalog, public_doc, write_catalog
from verify_standards import INDEX_LINK

ROOT = Path(__file__).resolve().parent.parent


class TestRcsMcpIndex(unittest.TestCase):
    def test_index_is_complete_and_provenanced(self):
        doc = (ROOT / "docs" / "standards.md").read_text(encoding="utf-8")
        reference = "0123456789abcdef0123456789abcdef01234567"
        catalog = build_catalog(ROOT, reference)
        rule_ids = [r["id"] for r in catalog["rules"]]
        self.assertEqual(rule_ids, [rule for rule, _ in INDEX_LINK.findall(doc)])
        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        self.assertTrue(rule_ids)
        self.assertEqual(catalog["revision"], reference)
        for rule in catalog["rules"]:
            with self.subTest(rule=rule["id"]):
                self.assertIn("## " + rule["id"], rule["markdown"])
                self.assertIn(reference, rule["source_url"])
                self.assertTrue(rule["url"].startswith("https://rcs.zevarix.com/rules/"))
                self.assertNotIn("W:/", rule["markdown"])
        self.assertEqual({g["id"] for g in catalog["guides"]}, set(GUIDES))
        self.assertTrue(all(any(line.startswith("# ") for line in g["markdown"].splitlines()) for g in catalog["guides"]))

    def test_catalog_bytes_are_deterministic(self):
        ref = "f" * 40
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            a, b = base / "a.json", base / "b.json"
            write_catalog(ROOT, a, ref)
            write_catalog(ROOT, b, ref)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            data = json.loads(a.read_text(encoding="utf-8"))
            self.assertNotIn("generated_at", data)

    def test_invalid_revision_rejected(self):
        for value in ("main", "HEAD", "../etc/passwd", "f" * 39, "z" * 40):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "commit SHA"):
                    build_catalog(ROOT, value)

    def test_noncanonical_documents_are_rejected(self):
        docs = ROOT / "docs"
        with self.assertRaisesRegex(ValueError, "Noncanonical"):
            public_doc(docs, "../README.md")
        with self.assertRaisesRegex(ValueError, "Noncanonical"):
            public_doc(docs, "missing-does-not-exist.md")


if __name__ == "__main__":
    unittest.main()
