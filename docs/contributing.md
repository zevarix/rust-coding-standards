# Proposing a rule or correction

This is a draft standards repository. Propose changes on an issue/branch and review the actual behavior before making any rule universal.

For new rules, supply a stable ID, applicability (required/advisory), scope, rationale, good/bad examples when relevant, an enforcement approach, and reasonable exceptions. When a preferred Rust block is self-contained, put `<!-- rcs-example: test -->` directly above its `rust` fence to compile and execute its tests, or `<!-- rcs-example: compile -->` to check a library example. Leave intentionally incorrect or schematic snippets **unmarked**. For claims about performance or safety, include the affected call path, a reproducible trigger and evidence, or clearly label the suggestion as exploratory.

Prefer minimal, broadly reusable principles over rules tied to one product, operating system or reviewer. No arbitrary file-length quotas or blanket tool/feature prohibitions. A new rule should make code easier to understand, test or maintain.

A project adopting these standards owns its own merge and release decisions. A reviewer finding here cannot authorize modifications or deployments in a consuming repository.

Before opening this repository to the public, choose a compatible license for original text and review every example for third-party rights, private details and accidental publication. Public visibility requires the owner's explicit approval.
