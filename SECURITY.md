# Security policy

RCS is primarily a standards/documentation repository with Python validators,
Rust examples and a documentation build workflow. It also provides an isolated,
publicly hosted **read-only MCP documentation service**. RCS is **not** a
credential store, private source reader, or security certification.

## Supported scope

Maintained source fixes target the current `main` branch. There is no tagged
public application release; the hosted MCP is packaged and deployed separately
at a versioned source revision reported by its public `/health` endpoint. The
live deployment need not equal the latest `main` revision.

A consumer application's vulnerabilities must be reported to that application's
maintainers, not assumed to be governed by RCS.

## Reporting a vulnerability privately

For a potential issue in an RCS validator, build workflow, public MCP transport
or tool definition, documentation behavior, or a concrete safety defect in an
RCS example:

1. If GitHub's repository **Security → Report a vulnerability** action is
   available, use it to submit a private vulnerability report.
2. If that private reporting feature is unavailable, use an already-known
   private channel to the repository owner. If you have none, open a minimal
   GitHub issue asking for a confidential reporting channel **without sharing
   exploit details, credentials, private paths or sensitive input**.

Do not assume an email address, a response-time guarantee, or a private
vulnerability-reporting feature has been configured. Private reports and
security-related repository settings require separate owner authority.

Please include a sanitized reproducer, affected source revision and
environment, impact, and mitigations when safely possible. Never include
third-party secrets or real user collections. Normal, non-sensitive rule
suggestions belong in regular issues and pull requests.

**Project and copyright holder:** Peder Klockmann (Zevarix).
