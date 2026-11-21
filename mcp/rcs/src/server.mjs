// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
//
// Public read-only RCS MCP endpoint. No user data, persistence, fetch, or
// write-capable tools. Rules are compiled from canonical Markdown at build.
import { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { getGuidance, getRule, metadata, revision, searchRules } from "./catalog.mjs";

const REFERENCE_SCHEMA = z.object({
  url: z.url(),
  source_url: z.url(),
});
const SOURCE_SCHEMA = REFERENCE_SCHEMA.extend({ revision: z.string() });
const SEARCH_RULE_SCHEMA = REFERENCE_SCHEMA.extend({
  id: z.string(),
  title: z.string(),
  level: z.string(),
  summary: z.string(),
});
const SEARCH_RESULT_SCHEMA = z.object({
  revision: z.string(),
  total_matches: z.number().int().min(0),
  rules: z.array(SEARCH_RULE_SCHEMA),
});
const RULE_RESULT_SCHEMA = SOURCE_SCHEMA.extend({
  id: z.string(),
  title: z.string(),
  level: z.string(),
  enforcement: z.string(),
  summary: z.string(),
  markdown: z.string(),
});
const GUIDE_RESULT_SCHEMA = SOURCE_SCHEMA.extend({
  id: z.string(),
  title: z.string(),
  markdown: z.string(),
});
const METADATA_RESULT_SCHEMA = z.object({
  revision: z.string(),
  index_url: z.url(),
  rule_count: z.number().int().min(0),
  guides: z.array(z.object({ id: z.string(), title: z.string(), url: z.url() })),
});
const readonly = {
  readOnlyHint: true,
  destructiveHint: false,
  openWorldHint: false,
  idempotentHint: true,
};

function success(data) {
  return {
    structuredContent: data,
    content: [{ type: "text", text: JSON.stringify(data) }],
  };
}

function unavailable(kind, id) {
  return {
    isError: true,
    content: [{ type: "text", text: kind + " not found in RCS revision " + revision + ": " + id }],
  };
}

export function createRcsServer() {
  const server = new McpServer({ name: "rcs-readonly", version: "0.1.0" });
  server.registerTool("search_rules", {
    description: "Search canonical RCS Rust rules by ID, topic, concern or behavior. Results cite the exact source revision; RCS is advisory unless a project adopts it.",
    inputSchema: z.object({
      query: z.string().trim().min(2).max(160),
      limit: z.number().int().min(1).max(20).default(8),
    }),
    outputSchema: SEARCH_RESULT_SCHEMA,
    annotations: readonly,
  }, async ({ query, limit }) => success(searchRules(query, limit)));

  server.registerTool("get_rule", {
    description: "Read one full, exact-ID RCS rule with required/advisory applicability, rationale, examples, and canonical source citation.",
    inputSchema: z.object({ rule_id: z.string().regex(/^RCS-[A-Z]+-\d{3}$/) }),
    outputSchema: RULE_RESULT_SCHEMA,
    annotations: readonly,
  }, async ({ rule_id }) => {
    const item = getRule(rule_id);
    return item ? success(item) : unavailable("Rule", rule_id);
  });

  server.registerTool("get_guidance", {
    description: "Read selected RCS adoption, review, verification, AI-code quality or performance workflow guidance from the exact canonical revision.",
    inputSchema: z.object({
      guide_id: z.enum([
        "adoption", "review-guide", "verification", "anti-ai-slop",
        "measurement", "profiling", "optimization",
      ]),
    }),
    outputSchema: GUIDE_RESULT_SCHEMA,
    annotations: readonly,
  }, async ({ guide_id }) => {
    const item = getGuidance(guide_id);
    return item ? success(item) : unavailable("Guide", guide_id);
  });

  server.registerTool("catalog_info", {
    description: "Return the exact RCS documentation commit, available guide names and rule index without reading any user's code or account.",
    inputSchema: z.object({}),
    outputSchema: METADATA_RESULT_SCHEMA,
    annotations: readonly,
  }, async () => success(metadata()));

  return server;
}
