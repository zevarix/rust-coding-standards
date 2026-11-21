# RCS read-only MCP server

This directory implements a genuine stateless Model Context Protocol server for
the public [Zevarix Rust Coding Standards](https://rcs.zevarix.com/) rules.

**Current release state:** Source implementation, loopback tests and portable
Node.js packaging only. **No Cloudflare or Hostinger deployment or public MCP
URL has been verified.** Do not claim the service is hosted merely because a
source branch is merged.

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
rejected, query/result sizes are bounded, and MCP Origin/Host handling is
provided by the current official Cloudflare Agents SDK handler.

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
No live Hostinger application has been created by the source release.

Build a small, versioned ZIP containing only pinned runtime dependencies,
the Node adapter, the read-only tool factory, generated catalog and licenses:

    python tools/package_rcs_hostinger.py

The generated `dist/rcs-hostinger-mcp-0.1.1.zip` is Git-ignored.
The GitHub Actions `rcs-hostinger-mcp` artifact on `main`
contains this **inner ZIP**; extract the Actions wrapper before uploading to
Hostinger. Rebuild from the selected release commit so the catalog identifies
the exact Git revision. The archive intentionally excludes the Cloudflare
CLI, Agents runtime, worktrees, tests, untrusted files and credentials.

Hostinger Business/Cloud web-app deployment uses a **new isolated Node.js
application**, framework `Other`, compatible Node.js 24.22+ (or
22.23+), `npm ci --omit=dev` and start command `npm start`
(running `node src/hostinger-entry.mjs`). Hostinger supplies `PORT`.
Set `NODE_ENV=production` and `RCS_PUBLIC_HOSTNAME` to the
hostname receiving requests. The proposed public hostname
`mcp.rcs.zevarix.com` is **not provisioned** by packaging.
`GET /health` exposes the Git revision, and `POST /mcp`
exposes stateless JSON-response Streamable HTTP without sessions.

Local and CI verification exercise a temporary loopback Node.js server,
real MCP initialization, tool discovery and lookup, hostile Host/Origin,
malformed input, and the 64 KiB request bound. CI also installs the
**extracted standalone ZIP** with production dependencies and tests it
independently of the source checkout.

**Hostinger release gate:** Verify a suitable existing Business/Cloud plan,
runtime compatibility, Node app capacity, DNS/subdomain ownership and
**no additional hosting purchase or charge** before creating or deploying
the app. Never overwrite the existing RCS documentation website or modify
unrelated sites, hosting settings, DNS or billing. Live activation and
public OpenAI plugin review remain separate, evidenced steps. The canonical
documentation website stays on GitHub Pages.

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
