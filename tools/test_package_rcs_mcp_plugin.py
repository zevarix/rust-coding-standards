#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Contract checks for a separate RCS MCP-backed plugin candidate."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from package_rcs_plugin import collect_files as existing_skills
from package_rcs_mcp_plugin import PACKAGE, MCP_URL, build, collect_files

ROOT = Path(__file__).resolve().parent.parent


class TestRcsConnectedPlugin(unittest.TestCase):
    def test_reproducible_complete_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.zip", Path(directory) / "b.zip"
            self.assertEqual(build(ROOT, first), build(ROOT, second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            expected = collect_files(ROOT)
            old = existing_skills(ROOT)
            with ZipFile(first) as archive:
                self.assertEqual(set(archive.namelist()), set(expected))
                self.assertIsNone(archive.testzip())
                for path, content in expected.items():
                    with self.subTest(path=path):
                        self.assertEqual(archive.read(path), content)
                self.assertEqual(
                    archive.read(f"{PACKAGE}/assets/forge-crab.png"),
                    old["rust-coding-standards/assets/forge-crab.png"]
                )
                for original, content in old.items():
                    if "/skills/" in original:
                        relative = original.split("/skills/", 1)[1]
                        self.assertEqual(archive.read(f"{PACKAGE}/skills/{relative}"), content)
                manifest = json.loads(archive.read(f"{PACKAGE}/plugin.json"))
                self.assertEqual(manifest["name"], PACKAGE)
                self.assertEqual(manifest["extensions"]["com.openai"]["interface"]["category"], "Developer Tools")
                cases = manifest["extensions"]["com.openai"]["review"]["test_cases"]
                self.assertEqual((len(cases["positive"]), len(cases["negative"])), (5, 3))
                self.assertEqual(
                    manifest["author"]["name"],
                    manifest["extensions"]["com.openai"]["interface"]["developerName"]
                )
                mcp = json.loads(archive.read(f"{PACKAGE}/mcp.json"))
                self.assertEqual(mcp["mcpServers"]["rcs"]["url"], MCP_URL)
                self.assertEqual(
                    mcp["mcpServers"]["rcs"]["extensions"]["com.openai"]["auth"],
                    {"type": "none"}
                )
                self.assertNotIn("apps", manifest["extensions"]["com.openai"])
                self.assertNotIn(f"{PACKAGE}/.app.json", archive.namelist())
            self.assertEqual(len(expected), len(old) + 1)

    def copy_sources(self, directory):
        target = Path(directory)
        shutil.copytree(ROOT / "plugin", target / "plugin")
        shutil.copytree(ROOT / "skills", target / "skills")
        return target

    def test_reject_wrong_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_sources(directory)
            path = repo / "plugin" / PACKAGE / "mcp.json"
            mcp = json.loads(path.read_text(encoding="utf-8"))
            mcp["mcpServers"]["rcs"]["url"] = "https://unapproved.example.com/mcp"
            path.write_text(json.dumps(mcp), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "endpoint or transport"):
                collect_files(repo)

    def test_reject_dropped_review_case(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_sources(directory)
            path = repo / "plugin" / PACKAGE / "plugin.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["extensions"]["com.openai"]["review"]["test_cases"]["positive"].pop()
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "five positive"):
                collect_files(repo)

    def test_reject_missing_canonical_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_sources(directory)
            (repo / "skills" / "rust-performance" / "NOTICE").unlink()
            with self.assertRaisesRegex(ValueError, "Unexpected/missing"):
                collect_files(repo)

    def test_checkout_line_endings_do_not_change_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            samples = []
            for name, ending in (("lf", b"\n"), ("crlf", b"\r\n")):
                repo = self.copy_sources(Path(directory) / name)
                for filename in ("plugin.json", "mcp.json"):
                    path = repo / "plugin" / PACKAGE / filename
                    text = path.read_bytes().replace(b"\r\n", b"\n")
                    path.write_bytes(text.replace(b"\n", ending))
                samples.append(repo)
            a, b = Path(directory) / "first.zip", Path(directory) / "second.zip"
            self.assertEqual(build(samples[0], a), build(samples[1], b))


if __name__ == "__main__":
    unittest.main()

