"""Keep RCS open-licensed materials distinct from the reserved Forge theme.

All tests are read-only and use Python's standard library. Licensing is
assigned by COPYRIGHT and the file-level notices, not by CI execution.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
OWNER = "2026 Peder Klockmann (Zevarix)"
SPDX = "MIT OR Apache-2.0"


class LicenseScopeTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_standard_dual_license_texts_and_ownership(self) -> None:
        mit = self.read("LICENSE-MIT")
        apache = self.read("LICENSE-APACHE")
        self.assertTrue(mit.startswith("Copyright (c) " + OWNER))
        self.assertIn("Permission is hereby granted", mit)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', mit)
        self.assertIn("Apache License", apache)
        self.assertIn("Version 2.0, January 2004", apache)
        self.assertIn("END OF TERMS AND CONDITIONS", apache)
        self.assertIn("Copyright (c) " + OWNER, self.read("COPYRIGHT"))
        self.assertIn("Copyright (c) " + OWNER, self.read("NOTICE"))

    def test_reservation_is_explicit_and_narrow(self) -> None:
        copyright_text = self.read("COPYRIGHT")
        reserved_license = self.read("LICENSE-FORGE-THEME")
        for rel in ("docs/stylesheets/forge.css", "docs/index.md"):
            self.assertIn(rel, copyright_text)
            self.assertIn(rel, reserved_license)
            self.assertIn(OWNER, self.read(rel))
            self.assertIn("rights reserved", self.read(rel).lower())
        self.assertIn("not licensed under", copyright_text.lower())
        self.assertIn("not covered", reserved_license.lower())
        self.assertIn("docs/assets/brand/forge-crab.svg", reserved_license)
        self.assertIn("MIT OR Apache-2.0", reserved_license)

    def test_crab_svg_is_open_and_attributed(self) -> None:
        svg = self.read("docs/assets/brand/forge-crab.svg")
        self.assertIn("SPDX-FileCopyrightText: " + OWNER, svg)
        self.assertIn("SPDX-License-Identifier: " + SPDX, svg)
        self.assertIn("<svg ", svg)
        self.assertIn("crab", svg.lower())

    def test_open_tooling_is_marked_but_reserved_theme_is_not(self) -> None:
        for rel in ("tools/verify_standards.py", "tools/verify_rust_examples.py",
                    "tools/test_verify_rust_examples.py",
                    "tools/test_sqlite_review_invariants.py"):
            value = self.read(rel)
            self.assertIn("SPDX-FileCopyrightText: " + OWNER, value)
            self.assertIn("SPDX-License-Identifier: " + SPDX, value)
        for rel in ("docs/stylesheets/forge.css", "docs/index.md"):
            self.assertNotIn("SPDX-License-Identifier: MIT OR Apache-2.0",
                             self.read(rel))

    def test_publication_remains_separately_owner_gated(self) -> None:
        readme = self.read("README.md")
        rights = self.read("docs/licensing.md")
        self.assertIn("MIT OR Apache-2.0", readme)
        self.assertIn("Peder Klockmann (Zevarix)", readme)
        self.assertIn("remain", rights.lower())
        self.assertIn("private", rights.lower())
        self.assertIn("public", rights.lower())
        self.assertIn("separate", rights.lower())
        self.assertIn("Licensing and reuse: licensing.md", self.read("mkdocs.yml"))
        self.assertIn("rights reserved", self.read("mkdocs.yml").lower())


if __name__ == "__main__":
    unittest.main()
