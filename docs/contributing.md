# Proposing a rule or correction

This is a draft standards repository. Propose changes on an issue/branch and review the actual behavior before making any rule universal.

Use [Q&A](https://github.com/zevarix/rust-coding-standards/discussions/categories/q-a)
for questions and [Ideas](https://github.com/zevarix/rust-coding-standards/discussions/categories/ideas)
for early suggestions. When the work is concrete, use the
[issue forms](https://github.com/zevarix/rust-coding-standards/issues/new/choose)
to propose a rule or report an RCS defect, then open a pull request with relevant
validation evidence. Keep examples synthetic and logs sanitized. Follow the
[security policy](https://github.com/zevarix/rust-coding-standards/blob/main/SECURITY.md)
for private vulnerability reports.

For new rules, supply a stable ID, applicability (required/advisory), scope, rationale, good/bad examples when relevant, an enforcement approach, and reasonable exceptions. When a preferred Rust block is self-contained, put `<!-- rcs-example: test -->` directly above its `rust` fence to compile and execute its tests, or `<!-- rcs-example: compile -->` to check a library example. Leave intentionally incorrect or schematic snippets **unmarked**. For claims about performance or safety, include the affected call path, a reproducible trigger and evidence, or clearly label the suggestion as exploratory.

Prefer minimal, broadly reusable principles over rules tied to one product, operating system or reviewer. No arbitrary file-length quotas or blanket tool/feature prohibitions. A new rule should make code easier to understand, test or maintain.

A project adopting these standards owns its own merge and release decisions. A reviewer finding here cannot authorize modifications or deployments in a consuming repository.

Original documentation, Rust examples, tools and crab artwork are contributed under **MIT OR Apache-2.0** unless different rights are specifically documented and accepted. Contributors retain copyright in their original work; document third-party source rights. The Forge CSS and authored homepage presentation are **rights reserved**, not ordinary open-source contributions; editing them requires separate rights coordination. See [Licensing and reuse](licensing.md). Public visibility still requires a separate explicit owner approval and source/history review.
