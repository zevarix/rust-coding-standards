// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
// Public Cloudflare Worker adapter for the shared RCS MCP tool factory.
import { createMcpHandler } from "agents/mcp/server";
import { metadata } from "./catalog.mjs";
import { createRcsServer } from "./server.mjs";
const MAX_RPC_BODY_BYTES = 64 * 1024;
export { createRcsServer } from "./server.mjs";

// A fresh MCP server is created for every request; no Durable Object, session,
// database, storage binding, authentication token or external service is needed.
const mcpHandler = createMcpHandler(createRcsServer, {
  route: "/mcp",
  responseMode: "json",
});

const safetyHeaders = {
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

function publicResponse(message, status = 200) {
  return new Response(JSON.stringify(message), {
    status,
    headers: { ...safetyHeaders, "content-type": "application/json; charset=utf-8" },
  });
}

async function limitedRpcRequest(request) {
  if (request.method !== "POST" || !request.body) return request;
  const declared = request.headers.get("content-length");
  if (declared && Number(declared) > MAX_RPC_BODY_BYTES) return null;

  const reader = request.body.getReader();
  const pieces = [];
  let total = 0;
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > MAX_RPC_BODY_BYTES) {
      await reader.cancel();
      return null;
    }
    pieces.push(value);
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const piece of pieces) {
    bytes.set(piece, offset);
    offset += piece.byteLength;
  }
  const headers = new Headers(request.headers);
  headers.delete("content-length");
  return new Request(request, { headers, body: bytes });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if ((url.pathname === "/" || url.pathname === "/health") && request.method === "GET") {
      const info = metadata();
      return publicResponse({
        name: "RCS read-only MCP",
        transport: "streamable-http",
        endpoint: "/mcp",
        revision: info.revision,
        rule_count: info.rule_count,
        guides: info.guides.map((g) => g.id),
        docs: info.index_url,
      });
    }
    if (url.pathname !== "/mcp") {
      return publicResponse({ error: "Not found", docs: "https://rcs.zevarix.com/" }, 404);
    }
    const bounded = await limitedRpcRequest(request);
    if (bounded === null) {
      return publicResponse({ error: "MCP request body exceeds 64 KiB" }, 413);
    }
    return mcpHandler(bounded, env, ctx);
  },
};
