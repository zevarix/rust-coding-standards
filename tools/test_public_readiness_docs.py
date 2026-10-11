"""Check that RCS public-readiness source docs remain honest and linked."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PublicationDocs(unittest.TestCase):
    def read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_public_onboarding_materials_exist(self) -> None:
        readme = self.read("README.md")
        for name in ("CONTRIBUTING.md", "SECURITY.md", "docs/publication-readiness.md"):
            self.assertTrue((ROOT / name).is_file(), name)
            self.assertIn(name, readme)

    def test_homepage_does_not_claim_nonadoption(self) -> None:
        homepage = self.read("docs/index.md")
        self.assertIn("Adopted by Retro Distro", homepage)
        self.assertNotIn("Not yet adopted", homepage)
        self.assertNotIn("Private working draft", homepage)
        self.assertIn("publication", homepage.lower())

    def test_readiness_does_not_authorize_exposure(self) -> None:
        readiness = self.read("docs/publication-readiness.md")
        self.assertIn("private", readiness.lower())
        self.assertIn("separately authorized", readiness.lower())
        self.assertIn("historical", readiness.lower())
        self.assertIn("reserved", readiness.lower())
        self.assertIn("MIT OR Apache-2.0", readiness)
        self.assertIn("Public-readiness checklist: publication-readiness.md",
                      self.read("mkdocs.yml"))
        self.assertIn("copyright", self.read("docs/licensing.md").lower())

    def test_security_reporting_without_invented_contact(self) -> None:
        sec = self.read("SECURITY.md")
        self.assertIn("Report a vulnerability", sec)
        self.assertIn("unavailable", sec)
        self.assertIn("without sharing", sec)
        self.assertIn("Peder Klockmann (Zevarix)", sec)

if __name__ == "__main__":
    unittest.main()
