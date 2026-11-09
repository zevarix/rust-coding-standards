---
name: rcs-guidance
description: Use when implementing or reviewing Rust in a project adopting Zevarix Rust Coding Standards, looking up an RCS rule, or deciding which RCS documentation applies to a task.
---

<!-- SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix) -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# RCS guidance

Find and apply relevant documentation from
[zevarix/rust-coding-standards](https://github.com/zevarix/rust-coding-standards).
Keep the consuming project's requirements, exceptions and authority local.

## Establish scope and revision

Read the project's instructions, owning work item and adoption declaration.
Identify the changed behavior, supported platforms and local safety contract.
If RCS is not adopted, use it as advice rather than inventing binding policy.

Resolve the chosen RCS reference: latest `main` when explicitly adopted, or
the consumer's intentional commit/tag. Record the actual commit inspected.
Read the index and relevant pages from that same resolved revision, including
cross-references. The installed skill's version does not override the
consumer's documentation reference. Do not create recurring SHA-update PRs
for a project following latest `main`.

Use an authorized GitHub integration or an existing qualified checkout at the
chosen revision. While the source is private, existing repository access is
required. If a route is unavailable, try another authorized read route;
identify inaccessible pages and continue safe work with that limitation.
Do not invent a successful documentation read, change credentials or copy
the whole rulebook into the consumer.

## Load the applicable documentation

These links locate canonical pages; substitute the resolved revision for
`main` when reading:

| Need | Start with |
| --- | --- |
| Locate rules and levels | [Standards index](https://github.com/zevarix/rust-coding-standards/blob/main/docs/standards.md) |
| Establish adoption and exceptions | [Adoption](https://github.com/zevarix/rust-coding-standards/blob/main/docs/adoption.md) |
| Review an exact candidate | [Review guide](https://github.com/zevarix/rust-coding-standards/blob/main/docs/review-guide.md) |
| Propose a shared correction | [Contributing](https://github.com/zevarix/rust-coding-standards/blob/main/docs/contributing.md) |

Follow index links to the rules relevant to the actual call path. Apply a
Required rule only when its conditions hold. Treat advisory guidance as a
review question, not an automatic blocker. Preserve stronger local
contracts and avoid unrelated refactoring.

For performance investigations, also load the `rust-performance` skill
when available, or its canonical source. Standards supply expectations;
the performance skill supplies the investigation method.

## Report with evidence

For each finding give: RCS revision and rule ID/link; path/symbol and call
path; concrete trigger; consequence; smallest correction and relevant
validation. Distinguish defects, suggestions and unknowns. State checks
actually performed and limitations.

A self-review is not an independent review. Passing RCS checks grants no
merge, deployment, publication or user-data mutation authority. Keep private
consumer evidence in that consumer's approved location and use only
sanitized examples in shared RCS contributions.
