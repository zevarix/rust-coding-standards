#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Safety and reproducibility checks for the standalone Hostinger MCP ZIP."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from package_rcs_hostinger import ALLOWED_DEPS, HOSTINGER_FILES, build, collect_files

ROOT = Path(__file__).resolve().parent.parent


class HostingerMcpPackageTests(unittest.TestCase):
    def test_deterministic_zip_and_canonical_public_files(self):
        with tempfile.TemporaryDirectory() as folder:
            one, two = Path(folder) / "one.zip", Path(folder) / "two.zip"
            self.assertEqual(build(ROOT, one), build(ROOT, two))
            self.assertEqual(one.read_bytes(), two.read_bytes())
            source = collect_files(ROOT)
            self.assertEqual(set(source), set(HOSTINGER_FILES))
            with ZipFile(one) as contents:
                self.assertIsNone(contents.testzip())
                self.assertEqual(set(contents.namelist()), set(source))
                for name, original in source.items():
                    with self.subTest(path=name):
                        self.assertEqual(contents.read(name), original)
                pkg = json.loads(contents.read("package.json"))
                lock = json.loads(contents.read("package-lock.json"))
                catalog = json.loads(contents.read("src/generated/catalog.json"))
                self.assertEqual(pkg["dependencies"], ALLOWED_DEPS)
                self.assertEqual(pkg["scripts"], {"start": "node src/node.mjs"})
                self.assertEqual(lock["packages"][""]["dependencies"], ALLOWED_DEPS)
                self.assertGreaterEqual(len(catalog["rules"]), 36)
                self.assertEqual(len(catalog["guides"]), 7)
                self.assertEqual(catalog["revision"], catalog["rules"][0]["source_url"].split("/blob/")[1][:40])
                self.assertNotIn("agents", pkg["dependencies"])
                self.assertNotIn("@cloudflare/vite-plugin", pkg["dependencies"])
                self.assertFalse(any(".env" in name or "node_modules" in name for name in contents.namelist()))

    def test_windows_line_endings_normalize_in_all_text_entries(self):
        payload = collect_files(ROOT)
        for name, original in payload.items():
            with self.subTest(path=name):
                self.assertNotIn(b"\r\n", original)
                self.assertNotIn(b"\r", original)


if __name__ == "__main__":
    unittest.main()
