#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Regression checks for reproducible, publicly safe RCS plugin exports."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from package_rcs_plugin import PACKAGE, SKILLS, SKILL_FILES, build, collect_files

ROOT = Path(__file__).resolve().parent.parent


class TestRcsPluginPackage(unittest.TestCase):
    def test_deterministic_archive_and_exact_canonical_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            first, second = dest / "first.zip", dest / "second.zip"
            self.assertEqual(build(ROOT, first), build(ROOT, second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            expected = collect_files(ROOT)
            with ZipFile(first) as z:
                self.assertEqual(set(z.namelist()), set(expected))
                self.assertIsNone(z.testzip())
                for path, content in expected.items():
                    with self.subTest(path=path):
                        self.assertEqual(z.read(path), content)
                manifest = json.loads(z.read(f"{PACKAGE}/plugin.json"))
                self.assertEqual(manifest["extensions"]["com.openai"]["interface"]["category"], "Developer Tools")
                self.assertNotIn("mcp.json", z.namelist())
                self.assertNotIn(".app.json", z.namelist())
            self.assertEqual(len(expected), 2 + len(SKILLS) * len(SKILL_FILES))

    def test_missing_skill_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            shutil.copytree(ROOT / "skills", temp / "skills")
            shutil.copytree(ROOT / "plugin", temp / "plugin")
            logo = temp / "docs" / "assets" / "brand"
            logo.mkdir(parents=True)
            shutil.copy2(ROOT / "docs" / "assets" / "brand" / "forge-crab.svg", logo / "forge-crab.svg")
            (temp / "skills" / "rcs-guidance" / "NOTICE").unlink()
            with self.assertRaisesRegex(ValueError, "Unexpected/missing"):
                build(temp, temp / "bundle.zip")

    def test_unreviewed_extra_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            shutil.copytree(ROOT / "skills", temp / "skills")
            shutil.copytree(ROOT / "plugin", temp / "plugin")
            logo = temp / "docs" / "assets" / "brand"
            logo.mkdir(parents=True)
            shutil.copy2(ROOT / "docs" / "assets" / "brand" / "forge-crab.svg", logo / "forge-crab.svg")
            (temp / "skills" / "rcs-guidance" / "unreviewed.txt").write_text("test-only", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unexpected/missing"):
                build(temp, temp / "bundle.zip")


if __name__ == "__main__":
    unittest.main()
