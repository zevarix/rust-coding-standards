// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
// Run against the extracted standalone Hostinger ZIP to detect missing files
// or production-only runtime dependency errors before shipping.
import assert from "node:assert/strict";
import { once } from "node:events";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const packageDir = process.argv[2];
if (!packageDir) throw new Error("Usage: node hostinger-standalone-smoke.mjs PATH_TO_EXTRACTED_ZIP");
const basePath = resolve(packageDir);
const { createNodeHttpServer } = await import(pathToFileURL(join(basePath, "src/node.mjs")).href);
const server = createNodeHttpServer();
server.listen(0, "127.0.0.1");
await once(server, "listening");
const base = "http://127.0.0.1:" + server.address().port;
async function rpc(id, method, params = {}) {
  const response = await fetch(base + "/mcp", {
    method: "POST",
    headers: {
      accept: "application/json, text/event-stream",
      "content-type": "application/json",
      "mcp-protocol-version": "2025-06-18",
    },
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
    signal: AbortSignal.timeout(8000),
  });
  return { status: response.status, result: await response.json() };
}
try {
  const healthResponse = await fetch(base + "/health", { signal: AbortSignal.timeout(8000) });
  assert.equal(healthResponse.status, 200);
  const health = await healthResponse.json();
  assert.ok(health.rule_count >= 36);
  assert.match(health.revision, /^[a-f0-9]{40}$/);
  assert.deepEqual(health.guides.length, 7);
  const initialized = await rpc(1, "initialize", {
    protocolVersion: "2025-06-18", capabilities: {},
    clientInfo: { name: "rcs-hostinger-archive-smoke", version: "0.1.0" },
  });
  assert.equal(initialized.status, 200);
  assert.equal(initialized.result.result.serverInfo.name, "rcs-readonly");
  const tools = await rpc(2, "tools/list");
  assert.equal(tools.status, 200);
  assert.deepEqual(new Set(tools.result.result.tools.map((x) => x.name)), new Set([
    "search_rules", "get_rule", "get_guidance", "catalog_info",
  ]));
  const rule = await rpc(3, "tools/call", { name: "get_rule", arguments: { rule_id: "RCS-PERF-001" } });
  assert.equal(rule.status, 200);
  assert.equal(rule.result.result.structuredContent.revision, health.revision);
  assert.match(rule.result.result.structuredContent.source_url, new RegExp(health.revision));
  console.log("PASS: extracted Hostinger archive starts, handshake, four tools, source revision and citations");
} finally {
  await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
}
