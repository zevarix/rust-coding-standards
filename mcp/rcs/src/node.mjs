// SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
// SPDX-License-Identifier: MIT OR Apache-2.0
//
// Hostinger Business/Cloud Node.js transport for the same read-only RCS MCP tools.
// No network fetching, user content, persistence or filesystem access at runtime.
import { createServer } from "node:http";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { NodeStreamableHTTPServerTransport } from "@modelcontextprotocol/node";
import { metadata } from "./catalog.mjs";
import { createRcsServer } from "./server.mjs";

const MAX_RPC_BODY_BYTES = 64 * 1024;
const PUBLIC_HOST = (process.env.RCS_PUBLIC_HOSTNAME || "mcp.rcs.zevarix.com").toLowerCase();
const LOOPBACK = new Set(["127.0.0.1", "localhost"]);
const HEADERS = {
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "content-type": "application/json; charset=utf-8",
};

function json(res, status, payload, headers = {}) {
  res.writeHead(status, { ...HEADERS, ...headers });
  res.end(JSON.stringify(payload));
}

function hostnameFromHostHeader(raw) {
  if (typeof raw !== "string" || !/^[a-z0-9.-]+(?::[0-9]{1,5})?$/i.test(raw)) return null;
  try {
    const host = new URL("http://" + raw).hostname.toLowerCase();
    return host === "localhost" || (/^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9-]+$/.test(host))
      ? host : (host === "127.0.0.1" ? host : null);
  } catch {
    return null;
  }
}

function allowedHost(req) {
  const host = hostnameFromHostHeader(req.headers.host);
  if (!host) return null;
  if (host === PUBLIC_HOST) return host;
  if (process.env.NODE_ENV !== "production" && LOOPBACK.has(host)) return host;
  return null;
}

function validOrigin(req, host) {
  const raw = req.headers.origin;
  if (raw === undefined) return true; // Server-to-server MCP clients omit Origin.
  if (typeof raw !== "string") return false;
  try {
    const parsed = new URL(raw);
    const localHttp = LOOPBACK.has(host) && process.env.NODE_ENV !== "production";
    return parsed.hostname.toLowerCase() === host &&
      ((parsed.protocol === "https:" && !parsed.port) ||
       (localHttp && parsed.protocol === "http:")) &&
      !parsed.username && !parsed.password &&
      parsed.pathname === "/" && !parsed.search && !parsed.hash;
  } catch {
    return false;
  }
}

async function readJsonBody(req) {
  const announced = req.headers["content-length"];
  if (announced !== undefined &&
      (!/^[0-9]+$/.test(announced) || Number(announced) > MAX_RPC_BODY_BYTES)) {
    return { status: 413, error: "MCP request body exceeds 64 KiB" };
  }
  const parts = [];
  let size = 0;
  try {
    for await (const chunk of req) {
      size += chunk.length;
      if (size > MAX_RPC_BODY_BYTES) return { status: 413, error: "MCP request body exceeds 64 KiB" };
      parts.push(chunk);
    }
    if (size === 0) return { status: 400, error: "Missing MCP JSON body" };
    return { parsed: JSON.parse(Buffer.concat(parts).toString("utf8")) };
  } catch {
    return { status: 400, error: "Invalid MCP JSON body" };
  }
}

export function createNodeHttpServer() {
  return createServer(async (req, res) => {
    const host = allowedHost(req);
    if (!host || !validOrigin(req, host)) {
      json(res, 403, { error: "Host or Origin not permitted" });
      return;
    }

    let path;
    try {
      path = new URL(req.url || "/", "http://" + req.headers.host).pathname;
    } catch {
      json(res, 400, { error: "Invalid request path" });
      return;
    }
    if (path === "/" || path === "/health") {
      if (req.method !== "GET") {
        json(res, 405, { error: "Method not allowed" }, { allow: "GET" });
        return;
      }
      const info = metadata();
      json(res, 200, {
        name: "RCS read-only MCP",
        transport: "streamable-http",
        endpoint: "/mcp",
        revision: info.revision,
        rule_count: info.rule_count,
        guides: info.guides.map((g) => g.id),
        docs: info.index_url,
      });
      return;
    }

    if (path !== "/mcp") {
      json(res, 404, { error: "Not found", docs: "https://rcs.zevarix.com/" });
      return;
    }
    if (req.method !== "POST") {
      json(res, 405, { error: "Stateless MCP accepts POST" }, { allow: "POST" });
      return;
    }
    const data = await readJsonBody(req);
    if (data.error) {
      json(res, data.status, { error: data.error });
      return;
    }
    const server = createRcsServer();
    const transport = new NodeStreamableHTTPServerTransport({
      sessionIdGenerator: undefined, // stateless; no user/session storage
      enableJsonResponse: true,
    });
    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, data.parsed);
    } catch {
      if (!res.headersSent) json(res, 500, { error: "MCP request processing failed" });
      else res.end();
    } finally {
      await transport.close();
      await server.close();
    }
  });
}

export function startNodeServer() {
  const rawPort = process.env.PORT || "3000";
  const port = Number(rawPort);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error("PORT must be a TCP port from 1 to 65535");
  }
  const server = createNodeHttpServer();
  server.listen(port, "0.0.0.0", () => {
    // Do not log tokens or requests. Hostinger's platform owns process lifecycle.
    console.info("RCS MCP ready on port " + port + "; public endpoint /mcp");
  });
  return server;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  startNodeServer();
}
