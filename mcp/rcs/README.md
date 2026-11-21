# RCS read-only MCP server

This directory implements a genuine stateless Model Context Protocol server for
the public [Zevarix Rust Coding Standards](https://rcs.zevarix.com/) rules.

**Current release state (November 20, 2026):** A standalone read-only
Node.js MCP service is **live on Hostinger** at the dedicated RCS hostname.
The Cloudflare Worker implementation remains tested but **undeployed**.

- **Public MCP (Streamable HTTP):** `https://rcsmcp.zevarix.com/mcp`
- **Health and revision:** <https://rcsmcp.zevarix.com/health>
- **Exact deployed RCS source revision:** `7a88387b636f5baf948ef8eb68adc907c4305077`
- **Hostinger Node.js release:** 24.x, standalone package v0.1.2.

The RCS documentation site stays on GitHub Pages. The MCP runs in a separate
Node.js application on already provisioned hosting, without a new subscription.
A previous temporary Hostinger hostname remains a functional fallback but is
not advertised as the canonical public endpoint. Public OpenAI Plugin Directory
approval is a separate process.

## Tools and scope

- `search_rules`: Search rule IDs, topics, and relevant explanation text.
- `get_rule`: Retrieve one full rule by exact `RCS-...` ID.
- `get_guidance`: Retrieve one public RCS workflow document by approved ID.
- `catalog_info`: List the available guides and the exact Git revision served.

Tools are **read-only**, stateless and unauthenticated because every returned
document is already publicly redistributable. No tool accepts a repository URL,
runs Rust, writes files, reads private user content or invokes an LLM. No
database, KV, R2, Durable Object, queue, cron, Workers AI, user tokens, or
long-lived MCP session is involved. The runtime embeds a generated copy of the
canonical Markdown from the specific source commit; it does **not** fetch
arbitrary URLs on request.

Each result cites the exact RCS GitHub source revision and a corresponding
public documentation page. RCS Required/Advisory labels apply only within a
consuming project's chosen adoption scope; the server does not grant review,
merge or execution authority.

The HTTP endpoint is `/mcp` (stateless Streamable HTTP). `/health` and `/` report
the bundle's source revision and catalog counts. Requests over 64 KiB are
rejected, and query/result sizes are bounded. Both transport adapters apply
Host and Origin checks: the Cloudflare transport uses the official Agents SDK
handler, while the Node.js adapter uses the official MCP Node transport with
explicit HTTP request validation.

## Local build and protocol test

Requires Python 3.12+, an exact compatible Node runtime (currently Node
24.22+ or 22.23+), and npm. Work inside this directory:

```sh
npm ci
npm test
npm run build
python test/protocol_smoke.py
```

`npm test` rebuilds the catalog from the current Git revision and checks
search, exact-rule lookups, link provenance, bounds, and errors. The protocol
smoke test uses a **loopback-only local Cloudflare Worker**. It proves an MCP
initialization handshake, tool discovery, calls, read-only annotations, schema
validation, oversized-body rejection, and Origin rejection; it stops the test
process when finished. It does not deploy.

The complete repository Python tests also check that every indexed rule
matches a real heading and index entry, and that output is deterministic.

Cloudflare CLI `cf` and Cloudflare Vite plugin v2 are pinned in
`package-lock.json` / `package.json`. No `wrangler.jsonc` is needed. The Worker
configuration is in `cloudflare.config.ts`; there are no paid bindings.

## Hostinger Business/Cloud Node.js deployment target

The repository also supports a **standalone Node.js Streamable HTTP MCP**
application, sharing the exact same four tool registrations and generated
source-revision-qualified catalog as the Cloudflare Worker. This is a separate
runtime option, not an additional tool provider or a rewritten standards set.
The Hostinger Node.js application is deployed to the RCS-specific public
hostname, separate from the RCS documentation site on GitHub Pages.

Build a small, versioned ZIP containing only pinned runtime dependencies,
the Node adapter, the read-only tool factory, generated catalog and licenses:

    python tools/package_rcs_hostinger.py

The generated `dist/rcs-hostinger-mcp-0.1.2.zip` is Git-ignored.
The GitHub Actions `rcs-hostinger-mcp` artifact on `main`
contains this **inner ZIP**; extract the Actions wrapper before uploading to
Hostinger. Rebuild from the selected release commit so the catalog identifies
the exact Git revision. The archive intentionally excludes the Cloudflare
CLI, Agents runtime, worktrees, tests, untrusted files and credentials.

Hostinger Business/Cloud web-app deployment uses a **new isolated Node.js
application**, framework `Other`, compatible Node.js 24.22+ (or
22.23+), and start command `npm start` (running
`node src/hostinger-entry.mjs`). Hostinger's archive builder installed
production dependencies via `npm install`; CI separately verifies
`npm ci --omit=dev` from the extracted ZIP. Hostinger supplies `PORT`.
Set `NODE_ENV=production` and configure `RCS_PUBLIC_HOSTNAME` to
a comma-separated list of **exact public DNS names**. For example:

    RCS_PUBLIC_HOSTNAME=rcsmcp.zevarix.com,temporary-mcp.example.com

The actual temporary fallback hostname is deployment configuration, not a
code or documentation dependency. The server rejects wildcards, malformed
names, URL forms, ports and IP addresses at startup. For every request,
Host must match an allowed name and any supplied Origin must match that
request's Host, including when both names are trusted.

Hostinger parks `rcsmcp.zevarix.com` on the **same** RCS Node.js
application, using its automatically managed DNS ALIAS and valid TLS certificate.
HTTP redirects to HTTPS. The original temporary endpoint was verified
functional after configuring both names. The generic `mcp.zevarix.com`
hostname remains unallocated for possible future services.

`GET /health` exposes the Git revision, and `POST /mcp`
exposes stateless JSON-response Streamable HTTP without sessions.

**Hostinger entrypoint caveat:** Its build-from-archive auto-detection
selected `src/server.mjs`, which is a tool factory and does not listen.
An earlier deployment with `src/node.mjs` also returned HTTP 503:
Hostinger imports entry modules instead of executing them as `argv[1]`.
Always configure the **exact build** with `node_version=24`,
`app_type=other`, `entry_file=src/hostinger-entry.mjs`,
`build_script=` empty and the versioned archive source.
The saved Hostinger build settings have since been corrected and read back
to `src/hostinger-entry.mjs`. Verify the actual entry on each future
deployment rather than assuming Hostinger's archive detector chose correctly.

Local and CI verification exercise a temporary loopback Node.js server,
real MCP initialization, tool discovery and lookup, hostile Host/Origin,
malformed input, and the 64 KiB request bound. CI also installs the
**extracted standalone ZIP** with production dependencies and tests it
independently of the source checkout.

**Live deployment verification (November 20, 2026):** An independent
external HTTPS client tested **both** the branded and temporary hostnames.
Each returned HTTP 200 for `/health` with the exact deployed source
revision, accepted Streamable HTTP MCP initialization and discovery of all four
read-only tools, and returned source-cited results for tool calls. Both hosts
correctly rejected malicious Origin, unsupported HTTP methods, unknown rules
and oversized request bodies. HTTP on the branded hostname redirects to HTTPS.

To repeat the public endpoint acceptance check from a separate Python client:

    python mcp/rcs/test/live_remote_smoke.py --base-url https://rcsmcp.zevarix.com --expected-revision 7a88387b636f5baf948ef8eb68adc907c4305077

Future deployments must use a reviewed source revision and verify the actual
Hostinger build entrypoint and both configured hostnames. Never overwrite
unrelated websites or change unrelated DNS or billing settings without
separate authority. GitHub integration is not hosting authority; public
OpenAI Plugin Directory review and publication remain separate steps.

## Explicit free-tier and deployment gate

Cloudflare's [Workers Free limits](https://developers.cloudflare.com/workers/platform/limits/)
currently include 100,000 requests/day and 10 ms CPU per invocation; Free
accounts reject usage exceeding the limit. The [Workers pricing
page](https://developers.cloudflare.com/workers/platform/pricing/) distinguishes
Workers Free from **Standard/Paid**, which can incur overage charges.

**Do not deploy unless the exact destination Cloudflare account is confirmed to
be on Workers Free, or the owner explicitly approves a different billable
exposure with enforceable spending controls.** A default usage model of
`standard` alone cannot establish a free/no-overage boundary. Neither a
successful local build nor a GitHub merge grants Cloudflare publication
authority.

When a zero-cost destination is verified, the release procedure is:

1. Verify the Cloudflare account/Workers plan and free limits using current
   account data. Do not alter an existing account-wide usage model, spend limit,
   DNS, unrelated Workers, or billing settings.
2. Confirm the target Worker name does not collide with an existing service.
3. Review the exact main commit and CI's catalog build, package lock, and
   protocol test, and qualify the Worker as a public read-only endpoint.
4. Deploy manually with `cf deploy` under that verified account (the npm
   `deploy` script intentionally refuses unqualified publishing). Prefer its
   first-party `workers.dev` hostname; a custom domain/DNS change is separate.
5. Read back the actual deployment and Worker settings, and test the public
   `/health`, Streamable HTTP tools, revision, and errors from an external
   client. Record the URL, commit, cost plan, and evidence on the owning issue.
6. Only then consider a **separate MCP-backed OpenAI plugin submission**.
   The existing skills-only plugin's public-directory intake status remains
   separate, and no fake MCP integration should be used to bypass that policy.

The canonical documentation website remains on **GitHub Pages** and is not
migrated by this service.
