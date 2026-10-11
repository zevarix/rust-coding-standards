# Zevarix Rust Guidelines

**Status: Draft 0.1 · Not yet adopted or released**

Practical, reusable coding standards for Rust applications and libraries. The aim is to offer the explicit rules, examples, and review consistency that a mature project coding standard provides—without excessive abstraction, arbitrary size limits, or tools that every project must purchase.

These guidelines are independently authored and informed by Rust's established ecosystem. They are **not** official Rust language standards, a safety certification scheme, or a replacement for a project's own design and safety requirements.

## Read the standards

Start with [the standards index](standards.md). Each rule has a stable ID, an applicability level, a reason, examples where useful, and a suggested enforcement method.

| Topic | Guide |
| --- | --- |
| Formatting, naming and module layout | [Style and structure](rules/style-and-structure.md) |
| Types, APIs and errors | [Types and errors](rules/types-and-errors.md) |
| Unsafe and external data boundaries | [Safety](rules/safety.md) |
| Real execution cost and readable efficiency | [Performance](rules/performance.md) |
| Deterministic verification | [Testing](rules/testing.md) |

## How adoption works

A project **opts in** to a pinned revision or eventual release; nothing here silently changes another repository's policy. See [adoption guidance and an example declaration](adoption.md). Projects own their toolchains, applicable rules, exceptions, code review, CI, and merge/release authority.

The defaults are deliberately modest:

- Use `rustfmt` rather than debating formatting.
- Follow the Rust API Guidelines where the API actually benefits.
- Use expressive types and ordinary `Result`-based errors.
- Review work performed across whole call paths, not just individual functions.
- Justify `unsafe` at its real invariant boundary.
- Test consequential failure paths with deterministic and safe fixtures.
- Prefer straightforward Rust over speculative abstractions and refactors.

**No file-length quotas, mandatory external reviewers, blanket recursion bans, or automatic prohibitions on language features.** An explicit standard should improve judgment, not replace it.

## Current development and public-readiness boundary

This repository began as a **private draft**. Visibility remains owner-controlled: **do not make it public without a separate explicit decision**.

Before any public release, review every example and reference for attribution and redistribution rights, decide an explicit license for the original documentation, remove any private material, and approve the first published version. No license or release is claimed yet.

References and their roles are listed in [SOURCES.md](sources.md). Proposed improvements are welcome as evidence-backed pull requests; see [CONTRIBUTING.md](contributing.md).
