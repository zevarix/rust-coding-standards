# Using Rust Coding Standards in code review

This guide explains how a reviewer uses the standards a project has **explicitly adopted**, normally from the **latest `main`**. Some projects may intentionally select a fixed revision. Either way, reviewers record the actual standards commit they consulted as evidence. This guide does not grant permission to change another repository, merge a pull request, publish a release or operate on user data.

## Start with the owning project

1. Read the consumer repository's current issue, applicable architecture and safety rules, exact reviewed base and HEAD, and available test evidence.
2. Confirm the project's own adoption declaration names **latest `main`** (or an intentionally fixed revision) and its scope. Resolve and record the actual RCS commit consulted for this review; do not require a project PR to keep the reference current. If the project has not adopted RCS, use the guidelines as suggestions or research—not invented mandatory merge gates.
3. Apply current owner-local requirements first. Resolve any conflict through the consumer's issue/decision process; a shared RCS rule never replaces a narrower product safety contract.

See [adoption](adoption.md) for the declaration format.

## Select applicable rules

Read the [standards index](standards.md), then open only the rules relevant to the changed behavior **and its surrounding call paths**. Do not mechanically apply every rule to every PR.

| Change touches | Start with |
| --- | --- |
| Naming, module boundaries or public APIs | [Style and structure](rules/style-and-structure.md), [Types and errors](rules/types-and-errors.md) |
| File sizes, offsets, budgets, index conversions or serialization widths | [Numbers and bounds](rules/numbers-and-bounds.md) |
| Unsafe code, external input or user-owned data | [Safety and user-owned data](rules/safety.md) |
| Filesystem identity, copying, publishing or uncertain retries | [Filesystem identity and completed effects](rules/mutable-effects.md) |
| External tools, subprocess output or cancellation | [Processes and cancellation](rules/processes-and-cancellation.md) |
| Concurrent writer admission or shared mutable state | [Concurrency and tooling](rules/concurrency-and-tooling.md) |
| Toolchain versions, format/lint or supported target checks | [Concurrency and tooling](rules/concurrency-and-tooling.md) |
| File hashing, expensive helpers, database requests or repeated batches | [Performance and execution cost](rules/performance.md) |
| Long-running work, terminal progress, verbose output or diagnostic logging | [Progress, diagnostics and logging](rules/observability.md) |
| Behavior changes, error paths or public contracts | [Testing and documentation](rules/testing.md) |

Follow the execution path far enough to understand effects. The diff tells you where code changed, not necessarily where the problem occurs. Tests and Clippy can confirm important properties, but passing them does not establish that a file copy, durable transition or large-data call path is correct.

## Classify a finding with evidence

An actionable review comment should state (and the PR/review should record the **RCS commit actually consulted** when applying RCS):

- **Rule:** exact ID, such as `RCS-NUM-001`, plus the owning project's stricter rule if applicable.
- **Where:** file and symbol, along with the call path or state transition that reaches it.
- **Trigger:** reproducible input, race, error, or realistic workload; do not invent facts or timings.
- **Consequence:** incorrect bytes, fabricated completion, rejected valid input, wasted I/O, or a specific maintenance hazard.
- **Smallest fix and test:** what would establish the required behavior without weakening other invariants.
- **Verification:** which checks were run on the exact reviewed revision and what has not been proven.

Severity follows the *consumer's* review policy. An evidence-backed correctness or data-safety failure generally needs a code change; a suggestion to rename a readable local helper normally does not. Advisory RCS rules are not automatic blockers. A Required rule also needs proof its applicability condition was met.

### Example: a concrete review finding

> **RCS-NUM-001 — consequential overflow.** `plan.rs::checked_end` computes `start + bytes` from an untrusted archive entry size. If the sum exceeds `u64::MAX`, behavior may panic or wrap depending on overflow settings, producing an invalid end offset. Return a range error from `checked_add`, and test both the largest valid span and an overflowing input.

The path and symbol above are illustrative, **not** a claim about any specific existing repository.

### Example: not a defect by itself

> "This file is long, and the code should use another trait."

Without a concrete comprehension problem, invariant risk, repeated work, or maintenance cost, this is an unsupported preference. Do not treat line counts, wrapper counts, or stylistic dissatisfaction as an acceptance criterion.

## Trace performance without weakening safety

For expensive code, name the entry point and count work **through called helpers**. Separate independent checks required at distinct points in time from redundant work against a demonstrably stable object. If one verified large file is streamed multiple times, quantify the number of passes and expected byte volume; do not invent throughput or optimization results.

For example, rehashing one 4-GiB source nine times implies roughly 36 GiB of logical source reads, **not** proof that the operation takes any particular number of seconds. Before removing a pass, show which identity, concurrency and freshness guarantees survive.

See [RCS-PERF-001](rules/performance.md#rcs-perf-001--review-work-across-call-paths).

## Write the review result

Use the verdict language required by the **owning project**. Distinguish verified defects, supported recommendations, and unverified questions. Be explicit about which platform, code path and evidence were not checked.

A normal implementation reviewer may perform self-review; an independent review must actually be performed by a separate reviewer or process before it can be described as independent. Neither result grants merge or release authority. If code changes after review, reevaluate the affected code and evidence against the new exact HEAD.

## Checking rulebook changes

Run the standard-library-only checker from the repository root whenever rule IDs, headings or links change:

```sh
python tools/verify_standards.py
zensical build
python tools/verify_standards.py --site
```

The first command checks the Markdown index and local links without a site builder. After installing the project's documented Zensical dependency, the build and second checker confirm that generated headings, links and search output exist. The validator discovers rules from their headings and index; it never requires a hardcoded total.

## Keep the rulebook maintainable

Do not copy the entire RCS text into a consuming review skill. Link to the consumer's **latest `main`** adoption (or intentional pin), read applicable pages before coding and during review, and record the actual RCS SHA used in review evidence. No recurring SHA-update PR is needed. Proposed changes to shared rules belong in this repository; each consumer retains its own code, policy, merge and release decisions.
