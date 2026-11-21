// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { once } from "node:events";
import { request } from "node:http";
import { createNodeHttpServer, parsePublicHostnames } from "../src/node.mjs";
import { metadata } from "../src/catalog.mjs";

test("public Host allowlist accepts exact names and fails closed on unsafe config", () => {
  const hosts = parsePublicHostnames(
    "solar-olive-mule-94.hostingersite.com, RCSMCP.ZEVARIX.COM "
  );
  assert.deepEqual([...hosts], [
    "solar-olive-mule-94.hostingersite.com",
    "rcsmcp.zevarix.com",
  ]);
  for (const bad of [
    "", " ", ",", "rcsmcp.zevarix.com,", "*.zevarix.com",
    "https://rcsmcp.zevarix.com", "rcsmcp.zevarix.com:443",
    "rcsmcp..zevarix.com", "localhost", "127.0.0.1",
    "rcsmcp.zevarix.com,https://attacker.example",
    "user@rcsmcp.zevarix.com",
  ]) {
    assert.throws(() => parsePublicHostnames(bad), { name: /Error/ }, bad);
  }
  assert.throws(() => parsePublicHostnames(null), TypeError);
});

test("Hostinger Node transport serves the same stateless read-only MCP catalog", async (t) => {
  const server = createNodeHttpServer();
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  t.after(async () => {
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  });
  const base = "http://127.0.0.1:" + server.address().port;

  async function call(method, path, payload, extra = {}) {
    const response = await fetch(base + path, {
      method,
      headers: {
        accept: "application/json, text/event-stream",
        "content-type": "application/json",
        "mcp-protocol-version": "2025-06-18",
        ...extra,
      },
      body: payload === undefined ? undefined : JSON.stringify(payload),
      signal: AbortSignal.timeout(8000),
    });
    const text = await response.text();
    return { status: response.status, body: JSON.parse(text), headers: response.headers };
  }

  async function rpc(id, method, params = {}) {
    return call("POST", "/mcp", { jsonrpc: "2.0", id, method, params });
  }

  const health = await call("GET", "/health");
  assert.equal(health.status, 200);
  assert.equal(health.body.rule_count, metadata().rule_count);
  assert.equal(health.body.revision, metadata().revision);
  assert.equal(health.headers.get("cache-control"), "no-store");
  const initialized = await rpc(1, "initialize", {
    protocolVersion: "2025-06-18",
    capabilities: {},
    clientInfo: { name: "rcs-hostinger-smoke", version: "0.1" },
  });
  assert.equal(initialized.status, 200, JSON.stringify(initialized.body));
  assert.equal(initialized.body.result.serverInfo.name, "rcs-readonly");

  const listed = await rpc(2, "tools/list");
  assert.equal(listed.status, 200, JSON.stringify(listed.body));
  assert.deepEqual(new Set(listed.body.result.tools.map((x) => x.name)), new Set([
    "search_rules", "get_rule", "get_guidance", "catalog_info",
  ]));
  for (const entry of listed.body.result.tools) {
    assert.equal(entry.annotations.readOnlyHint, true);
    assert.equal(entry.annotations.destructiveHint, false);
    assert.equal(entry.annotations.openWorldHint, false);
  }

  async function invoke(id, name, args = {}) {
    const reply = await rpc(id, "tools/call", { name, arguments: args });
    assert.equal(reply.status, 200, JSON.stringify(reply.body));
    return reply.body.result;
  }
  const info = await invoke(3, "catalog_info");
  assert.equal(info.structuredContent.revision, metadata().revision);
  const search = await invoke(4, "search_rules", { query: "RCS-PERF-001" });
  assert.equal(search.structuredContent.rules[0].id, "RCS-PERF-001");
  const rule = await invoke(5, "get_rule", { rule_id: "RCS-PERF-001" });
  assert.match(rule.structuredContent.source_url, new RegExp(metadata().revision));
  const guide = await invoke(6, "get_guidance", { guide_id: "optimization" });
  assert.match(guide.structuredContent.source_url, new RegExp(metadata().revision));
  const absent = await invoke(7, "get_rule", { rule_id: "RCS-FAKE-999" });
  assert.equal(absent.isError, true);
  const badArguments = await rpc(8, "tools/call", {
    name: "search_rules", arguments: { query: "x", limit: 999 },
  });
  assert.equal(badArguments.status, 200);
  assert.equal(badArguments.body.result.isError, true);

  assert.equal((await call("GET", "/mcp")).status, 405);
  assert.equal((await call("POST", "/absent", {})).status, 404);
  assert.equal((await call("POST", "/mcp", {}, { origin: "https://malicious.example" })).status, 403);
  const oversizedAnnounced = await new Promise((resolve, reject) => {
    const body = JSON.stringify({ padding: "x".repeat(65_537) });
    const req = request(base + "/mcp", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
        "content-length": Buffer.byteLength(body),
      },
    }, (res) => {
      res.resume();
      res.once("end", () => resolve(res.statusCode));
    });
    req.once("error", reject);
    req.end(body);
  });
  assert.equal(oversizedAnnounced, 413);
  const malformed = await fetch(base + "/mcp", {
    method: "POST", headers: { "content-type": "application/json" }, body: "{bad json",
  });
  assert.equal(malformed.status, 400);
  const oversized = await call("POST", "/mcp", { padding: "x".repeat(70_000) });
  assert.equal(oversized.status, 413);

  const hostileHost = await new Promise((resolve, reject) => {
    const req = request(base + "/health", { headers: { host: "attacker.example" } }, (res) => {
      res.resume();
      res.once("end", () => resolve(res.statusCode));
    });
    req.once("error", reject);
    req.end();
  });
  assert.equal(hostileHost, 403);
});
