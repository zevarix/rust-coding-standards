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
                interface = manifest["extensions"]["com.openai"]["interface"]
                self.assertEqual(interface["category"], "Developer Tools")
                self.assertEqual(manifest["author"]["name"], interface["developerName"])
                self.assertEqual(interface["logo"], "./assets/forge-crab.png")
                image = z.read(f"{PACKAGE}/assets/forge-crab.png")
                self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(len(manifest["extensions"]["com.openai"]["review"]["prompts"]), 3)
                self.assertTrue(manifest["extensions"]["com.openai"]["publication"]["release_notes"])
                self.assertNotIn("mcp.json", z.namelist())
                self.assertNotIn(".app.json", z.namelist())
            self.assertEqual(len(expected), 2 + len(SKILLS) * len(SKILL_FILES))

    def test_manifest_checkout_line_endings_do_not_change_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            sources = []
            for name, ending in (("lf", b"\n"), ("crlf", b"\r\n")):
                repo = directory / name
                shutil.copytree(ROOT / "skills", repo / "skills")
                shutil.copytree(ROOT / "plugin", repo / "plugin")
                manifest = repo / "plugin" / PACKAGE / "plugin.json"
                canonical = manifest.read_bytes().replace(b"\r\n", b"\n")
                manifest.write_bytes(canonical.replace(b"\n", ending))
                sources.append(repo)
            first, second = directory / "lf.zip", directory / "crlf.zip"
            self.assertEqual(build(sources[0], first), build(sources[1], second))
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_missing_skill_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            shutil.copytree(ROOT / "skills", temp / "skills")
            shutil.copytree(ROOT / "plugin", temp / "plugin")
            (temp / "skills" / "rcs-guidance" / "NOTICE").unlink()
            with self.assertRaisesRegex(ValueError, "Unexpected/missing"):
                build(temp, temp / "bundle.zip")

    def test_corrupt_public_icon_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            shutil.copytree(ROOT / "skills", temp / "skills")
            shutil.copytree(ROOT / "plugin", temp / "plugin")
            (temp / "plugin" / PACKAGE / "assets" / "forge-crab.png").write_bytes(
                b"not a PNG" * 4
            )
            with self.assertRaisesRegex(ValueError, "not a valid PNG"):
                build(temp, temp / "bundle.zip")

    def test_unreviewed_extra_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            shutil.copytree(ROOT / "skills", temp / "skills")
            shutil.copytree(ROOT / "plugin", temp / "plugin")
            (temp / "skills" / "rcs-guidance" / "unreviewed.txt").write_text("test-only", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unexpected/missing"):
                build(temp, temp / "bundle.zip")


if __name__ == "__main__":
    unittest.main()
