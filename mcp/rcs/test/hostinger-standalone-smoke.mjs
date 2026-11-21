// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
// Test exactly the extracted Hostinger ZIP via a dynamic import into a
// separate Node runner process: Hostinger imports the entrypoint; it does not
// execute it as process.argv[1]. This catches accidental argv guards.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { createServer, request } from "node:http";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";

const packageDir = process.argv[2];
if (!packageDir) throw new Error("Usage: node hostinger-standalone-smoke.mjs PATH_TO_EXTRACTED_ZIP");
const basePath = resolve(packageDir);
const entry = pathToFileURL(join(basePath, "src/hostinger-entry.mjs")).href;
const host = "rcs-hostinger-smoke.example.com";
const alternateHost = "rcsmcp-alias.example.com";
const brandedHost = "rcsmcp.zevarix.com";
const syntheticChallenge = "synthetic-review-challenge-456";

const probe = createServer();
probe.listen(0, "127.0.0.1");
await once(probe, "listening");
const port = probe.address().port;
await new Promise((resolveClose, reject) =>
  probe.close((error) => error ? reject(error) : resolveClose()));

let captured = "";
const child = spawn(process.execPath,
  ["--input-type=module", "--eval", "await import(" + JSON.stringify(entry) + ")"],
  {
    cwd: basePath,
    env: {
      ...process.env,
      NODE_ENV: "production",
      RCS_PUBLIC_HOSTNAME: host + ", " + alternateHost + ", " + brandedHost,
      RCS_OPENAI_APPS_CHALLENGE_TOKEN: syntheticChallenge,
      PORT: String(port),
    },
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  },
);
for (const stream of [child.stdout, child.stderr]) {
  stream.on("data", (bytes) => {
    if (captured.length < 8192) captured += bytes.toString("utf8");
  });
}

async function send(method, path, payload, headerOverrides = {}, parseJson = true) {
  const body = payload === undefined ? undefined : JSON.stringify(payload);
  return new Promise((fulfill, reject) => {
    const req = request({
      hostname: "127.0.0.1",
      port,
      path,
      method,
      headers: {
        host,
        accept: "application/json, text/event-stream",
        "content-type": "application/json",
        "mcp-protocol-version": "2025-06-18",
        ...headerOverrides,
      },
    }, (res) => {
      const chunks = [];
      res.on("data", (part) => chunks.push(part));
      res.once("end", () => {
        const raw = Buffer.concat(chunks).toString("utf8");
        try {
          fulfill({ status: res.statusCode, body: parseJson ? JSON.parse(raw) : raw, headers: res.headers });
        } catch {
          reject(new Error("Non-JSON HTTP response: " + raw.slice(0, 200)));
        }
      });
      res.once("error", reject);
    });
    req.setTimeout(5000, () => req.destroy(new Error("HTTP request timed out")));
    req.once("error", reject);
    req.end(body);
  });
}

const rpc = (id, method, params = {}) =>
  send("POST", "/mcp", { jsonrpc: "2.0", id, method, params });

try {
  let ready = false;
  for (let i = 0; i < 80; i++) {
    if (child.exitCode !== null) throw new Error("Node runner exited: " + child.exitCode + "\n" + captured);
    try {
      const health = await send("GET", "/health");
      if (health.status === 200) {
        assert.ok(health.body.rule_count >= 36);
        assert.match(health.body.revision, /^[a-f0-9]{40}$/);
        assert.equal(health.body.guides.length, 7);
        ready = true;
        break;
      }
    } catch {
      // Expected until the Node app begins listening.
    }
    await new Promise((done) => setTimeout(done, 80));
  }
  if (!ready) throw new Error("Imported Node entry did not call listen()\n" + captured);

  const challenge = await send("GET", "/.well-known/openai-apps-challenge", undefined,
    { host: brandedHost }, false);
  assert.equal(challenge.status, 200);
  assert.equal(challenge.body, syntheticChallenge);
  assert.match(challenge.headers["content-type"], /^text\/plain/);
  assert.equal((await send("GET", "/.well-known/openai-apps-challenge", undefined,
    { host: alternateHost })).status, 404);
  assert.equal((await send("GET", "/.well-known/openai-apps-challenge", undefined,
    { host: brandedHost, origin: "https://attacker.example" })).status, 403);
  assert.equal((await send("POST", "/.well-known/openai-apps-challenge", undefined,
    { host: brandedHost })).status, 405);

  const initialized = await rpc(1, "initialize", {
    protocolVersion: "2025-06-18",
    capabilities: {},
    clientInfo: { name: "hostinger-archive-import-smoke", version: "0.1.0" },
  });
  assert.equal(initialized.status, 200, JSON.stringify(initialized.body));
  assert.equal(initialized.body.result.serverInfo.name, "rcs-readonly");

  const listed = await rpc(2, "tools/list");
  assert.equal(listed.status, 200, JSON.stringify(listed.body));
  assert.deepEqual(
    new Set(listed.body.result.tools.map((x) => x.name)),
    new Set(["search_rules", "get_rule", "get_guidance", "catalog_info"]),
  );
  for (const item of listed.body.result.tools) {
    assert.equal(item.annotations.readOnlyHint, true);
    assert.equal(item.annotations.destructiveHint, false);
  }
  const rule = await rpc(3, "tools/call", {
    name: "get_rule", arguments: { rule_id: "RCS-PERF-001" },
  });
  assert.equal(rule.status, 200, JSON.stringify(rule.body));
  const health = await send("GET", "/health");
  assert.equal(rule.body.result.structuredContent.revision, health.body.revision);
  assert.match(rule.body.result.structuredContent.source_url, new RegExp(health.body.revision));
  const aliasHealth = await send("GET", "/health", undefined, { host: alternateHost });
  assert.equal(aliasHealth.status, 200);
  assert.equal(aliasHealth.body.revision, health.body.revision);
  const aliasInitialize = await send("POST", "/mcp", {
    jsonrpc: "2.0", id: 4, method: "initialize", params: {
      protocolVersion: "2025-06-18", capabilities: {},
      clientInfo: { name: "rcs-alias-smoke", version: "0.1.2" },
    },
  }, { host: alternateHost, origin: "https://" + alternateHost });
  assert.equal(aliasInitialize.status, 200, JSON.stringify(aliasInitialize.body));
  assert.equal(aliasInitialize.body.result.serverInfo.name, "rcs-readonly");
  const crossHostOrigin = await send("POST", "/mcp", {
    jsonrpc: "2.0", id: 5, method: "tools/list",
  }, { host, origin: "https://" + alternateHost });
  assert.equal(crossHostOrigin.status, 403);
  const blocked = await send("GET", "/health", undefined, { host: "attacker.example" });
  assert.equal(blocked.status, 403);
  const hostileOrigin = await send("POST", "/mcp", { jsonrpc: "2.0", id: 4, method: "tools/list" },
    { origin: "https://attacker.example" });
  assert.equal(hostileOrigin.status, 403);
  console.log("PASS: imported Hostinger app, two trusted hosts, real MCP handshake, four tools, citations and Host/Origin guards");
} finally {
  if (child.exitCode === null) {
    child.kill();
    await Promise.race([
      once(child, "exit"),
      new Promise((done) => setTimeout(done, 3000)),
    ]);
  }
}
