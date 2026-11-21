// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
//
// Pure, bounded reads over a catalog generated from canonical RCS Markdown.
// There is no repository access, outbound fetch, persistence or user data.
import catalog from "./generated/catalog.json" with { type: "json" };

const MAX_QUERY_LENGTH = 160;
const MAX_RESULTS = 20;
const ruleById = new Map(catalog.rules.map((rule) => [rule.id, rule]));
const guideById = new Map(catalog.guides.map((guide) => [guide.id, guide]));

if (ruleById.size !== catalog.rules.length) {
  throw new Error("Invalid bundled RCS catalog: duplicate rule IDs");
}

export const revision = catalog.revision;

export function metadata() {
  return {
    revision: catalog.revision,
    index_url: catalog.index_url,
    rule_count: catalog.rules.length,
    guides: catalog.guides.map(({ id, title, url }) => ({ id, title, url })),
  };
}

export function searchRules(query, limit = 8) {
  if (typeof query !== "string" || query.trim().length < 2 || query.length > MAX_QUERY_LENGTH) {
    throw new RangeError("Search query must contain 2 to 160 characters");
  }
  if (!Number.isInteger(limit) || limit < 1 || limit > MAX_RESULTS) {
    throw new RangeError("Search result limit must be between 1 and 20");
  }
  const normalized = query.toLocaleLowerCase("en-US").trim();
  const terms = normalized.split(/\s+/u).filter(Boolean);
  const matches = [];
  for (const rule of catalog.rules) {
    const title = rule.title.toLocaleLowerCase("en-US");
    const description = rule.summary.toLocaleLowerCase("en-US");
    const body = rule.markdown.toLocaleLowerCase("en-US");
    const id = rule.id.toLocaleLowerCase("en-US");
    const searchable = id + " " + title + " " + description + " " + body;
    if (!terms.every((term) => searchable.includes(term))) continue;
    const score =
      (id === normalized ? 1000 : id.includes(normalized) ? 250 : 0) +
      terms.reduce((acc, term) => acc + (title.includes(term) ? 20 : 0) +
        (description.includes(term) ? 10 : 0) + (id.includes(term) ? 6 : 0), 0);
    matches.push({ score, rule });
  }
  matches.sort((a, b) => b.score - a.score || a.rule.id.localeCompare(b.rule.id));
  return {
    revision: catalog.revision,
    total_matches: matches.length,
    rules: matches.slice(0, limit).map(({ rule }) => ({
      id: rule.id,
      title: rule.title,
      level: rule.level,
      summary: rule.summary,
      url: rule.url,
      source_url: rule.source_url,
    })),
  };
}

export function getRule(ruleId) {
  if (typeof ruleId !== "string" || !/^RCS-[A-Z]+-\d{3}$/.test(ruleId)) {
    return null;
  }
  const rule = ruleById.get(ruleId);
  if (!rule) return null;
  return {
    revision: catalog.revision,
    id: rule.id,
    title: rule.title,
    level: rule.level,
    enforcement: rule.enforcement,
    summary: rule.summary,
    markdown: rule.markdown,
    url: rule.url,
    source_url: rule.source_url,
  };
}

export function getGuidance(guideId) {
  if (typeof guideId !== "string" || !/^[a-z][a-z-]{0,39}$/.test(guideId)) {
    return null;
  }
  const guide = guideById.get(guideId);
  if (!guide) return null;
  return {
    revision: catalog.revision,
    id: guide.id,
    title: guide.title,
    markdown: guide.markdown,
    url: guide.url,
    source_url: guide.source_url,
  };
}
