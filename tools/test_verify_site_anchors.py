#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Ensure rule anchors survive valid HTML minification syntax."""
import unittest

from verify_standards import html_element_ids


class TestHtmlElementIds(unittest.TestCase):
    def test_quoted_unquoted_and_single_quoted_ids(self):
        html = """<h2 id="rcs-a-001"></h2><h2 id=rcs-b-001></h2><p id='content'></p>"""
        self.assertEqual(html_element_ids(html), {"rcs-a-001", "rcs-b-001", "content"})

    def test_only_element_attributes_count(self):
        html = '<!-- <h2 id=phantom> --> <script>let s = "id=bogus";</script><h2>no id</h2>'
        self.assertEqual(html_element_ids(html), set())


if __name__ == "__main__":
    unittest.main()
