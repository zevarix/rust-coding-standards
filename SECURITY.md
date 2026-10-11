# Security policy

RCS is primarily a standards/documentation repository with Python validators,
Rust examples and a documentation build workflow. It is **not** a credential
store, security certification, or a production service.

## Supported scope

There is no versioned public release yet. Maintained fixes target the current
`main` branch. A consumer application's vulnerabilities must be reported to
that application's maintainers, not assumed to be governed by RCS.

## Reporting a vulnerability privately

For a potential issue in a validator, build workflow, documentation behavior,
or a concrete safety defect in an RCS example:

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
