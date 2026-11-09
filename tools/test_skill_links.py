# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Exercise repository-local skill links through the source validator."""
from pathlib import Path
import tempfile
import unittest

from verify_standards import validate


class SkillLinkTests(unittest.TestCase):
    def fixture(self, root: Path, reference_exists: bool) -> None:
        files = {
            "docs/standards.md":
                "| [RCS-PERF-999](rules/example.md#rcs-perf-999--example) |\n",
            "docs/rules/example.md":
                "## RCS-PERF-999 — Example {#rcs-perf-999--example}\n",
            "docs/review-guide.md": "# Review\n",
            "mkdocs.yml":
                "nav:\n  - Rule: rules/example.md\n  - Review: review-guide.md\n",
            "skills/example/SKILL.md": "[Reference](references/detail.md)\n",
        }
        if reference_exists:
            files["skills/example/references/detail.md"] = "# Detail\n"
        for name, value in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")

    def test_reports_missing_skill_reference(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root, reference_exists=False)
            errors = validate(root, verify_site=False)
            self.assertTrue(any(
                "skills/example/SKILL.md: broken relative link" in error.replace("\\", "/")
                for error in errors
            ), errors)

    def test_accepts_existing_skill_reference(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root, reference_exists=True)
            self.assertEqual([], validate(root, verify_site=False))


if __name__ == "__main__":
    unittest.main()
