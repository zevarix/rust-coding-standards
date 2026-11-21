// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { getGuidance, getRule, metadata, revision, searchRules } from "../src/catalog.mjs";

test("catalog is source-revision-qualified and exposes known guides", () => {
  const info = metadata();
  assert.match(info.revision, /^[a-f0-9]{40}$/);
  assert.equal(info.revision, revision);
  assert.ok(info.rule_count > 0);
  assert.ok(info.guides.some((guide) => guide.id === "optimization"));
  assert.ok(info.guides.some((guide) => guide.id === "review-guide"));
});

test("exact rule lookup returns source-cited Rust guidance", () => {
  const rule = getRule("RCS-PERF-001");
  assert.equal(rule.id, "RCS-PERF-001");
  assert.ok(rule.markdown.includes("entire action path"));
  assert.match(rule.source_url, new RegExp(revision));
  assert.match(rule.url, /^https:\/\/rcs\.zevarix\.com\/rules\//);
  assert.equal(getRule("RCS-DOES-NOT-EXIST"), null);
  assert.equal(getRule("../etc/passwd"), null);
  assert.equal(getRule("rcs-perf-001"), null);
});

test("search ranks exact IDs and bounds result counts", () => {
  const found = searchRules("RCS-PERF-001");
  assert.equal(found.rules[0].id, "RCS-PERF-001");
  assert.ok(found.total_matches >= 1);
  const many = searchRules("RCS", 3);
  assert.equal(many.rules.length, 3);
  assert.ok(many.total_matches >= 3);
  assert.ok(many.rules.every((rule) => !("markdown" in rule)));
  const none = searchRules("unique-unlikely-query-cant-match", 5);
  assert.equal(none.rules.length, 0);
  assert.equal(none.total_matches, 0);
});

test("malformed or overly broad tool requests fail closed", () => {
  for (const bad of ["", " ", "x", "x".repeat(161), null, 7]) {
    assert.throws(() => searchRules(bad), RangeError);
  }
  for (const n of [0, -1, 21, 2.5, "3", null]) {
    assert.throws(() => searchRules("Rust", n), RangeError);
  }
});

test("guidance can be fetched only from fixed, public topics", () => {
  const guide = getGuidance("verification");
  assert.ok(guide.markdown.includes("Risk-weighted behavioral verification"));
  assert.match(guide.source_url, new RegExp(revision));
  assert.equal(getGuidance("../../.env"), null);
  assert.equal(getGuidance("missing"), null);
});
