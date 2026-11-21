---
title: "Anti AI Slop Rust: Review AI-Generated Code"
description: "Practical anti-AI-slop Rust code review: eliminate redundant work, preserve correctness, verify tests, and measure performance for human and AI-written Rust."
tags:
  - AI-assisted Development
  - Performance
  - Testing
---

# Anti AI Slop Rust: Build Correct, Fast Rust Without Needless Complexity

**Anti AI Slop Rust** is a practical approach to reviewing generated or human-written Rust for demonstrable problems: unnecessary layers, repeated expensive work, fragile error paths, and tests that do not prove the intended behavior. The goal is not to reject AI-generated code. It is to demand the *same engineering quality* from every contributor.

The [Rust Coding Standards index](standards.md) supplies individually scoped rules and links. The guidance below is a focused way to apply them when a patch looks convincing but may be unnecessarily slow, hard to maintain, or incorrect.

## What should a good Rust change achieve?

A useful change makes an observable behavior correct, is understandable to the next maintainer, and handles realistic failure conditions without inventing unrelated complexity. If the code processes a batch, archives, large files, network responses, or database transactions, it should also consider **how the total work scales** from the outset.

A reviewer should establish five things:

1. **Contract:** What input, output, state transition or error does the change promise? Are valid inputs accidentally rejected or invalid inputs accepted?
2. **Ownership:** Who owns mutable state, resources and side effects? Are filesystem and transaction boundaries current when consequential actions occur?
3. **Cost:** How often is expensive work performed, including inside helper calls? Are reads, parses, hashes, allocations or SQL preparations repeated without a new fact to establish?
4. **Evidence:** Do positive, negative and interruption tests actually assert the behavior? Has the implementation been exercised on supported platforms?
5. **Trade-off:** Is the chosen algorithm or abstraction simpler than its alternatives without sacrificing the verified contract?

These questions align with [RCS-PERF-001](rules/performance.md#rcs-perf-001--review-work-across-call-paths), [RCS-TEST-004](rules/testing.md#rcs-test-004--verify-consequential-behavior-not-only-execution), and the [review guide](review-guide.md).

## Avoid the repeated-validation trap

Redundant checking is not automatically safer. An agent can add several helpers that independently parse the same stable input, read the same immutable data, or reprepare the same SQL statement. Those operations can compound across hundreds or thousands of items.

For an **immutable or correctly held observation**, this is often needlessly expensive:

```rust
// Illustrative: inspect() reads and analyzes the same stable input twice.
let length = inspect(&snapshot)?.length;
let digest = inspect(&snapshot)?.digest;
```

Where the snapshot is demonstrably stable for both uses, reuse the qualified result instead:

```rust
let inspected = inspect(&snapshot)?;
let length = inspected.length;
let digest = inspected.digest;
```

**Important:** A mutable filesystem path, native handle, database record, or source collection may change between observation and effect. Do not reuse stale evidence across a fresh authorization, publication, transaction, or recovery boundary. Each necessary check must prove a *different required fact* or a fact that could have changed. See [filesystem identity](rules/mutable-effects.md) and [completed effects and recovery](rules/mutable-effects.md#rcs-state-002--reconcile-uncertain-effects-before-retrying-them).

The review question is not "how can we delete more checks?" It is **"what does this check establish, and can we prove it without repeated full work?"**

## Design for performance before profiling

Before introducing a worker pool, cache, adapter hierarchy or elaborate type wrapper, ask whether a simpler algorithm avoids the bottleneck entirely. Trace the *whole action*, not just the changed function: a supposedly cheap helper can trigger disk scans, decompression, database writes, synchronization or repeated hashing.

Performance decisions should consider total operations, input size, memory retention, contention and worst-case growth. Optimization must follow meaningful measurements rather than an arbitrary line-count reduction or a model's predicted speedup.

The [Rust performance skill](skills.md) provides an investigation workflow. Our [measurement guide](performance/measurement.md) explains comparable baselines, diagnostic overhead, fresh owned fixtures and truthful speedup claims.

## Tests are allowed—and expected—to evolve

**Never prohibit updating tests just because a change is an optimization.** Tests should be added, corrected, refactored or replaced when an approved behavior or implementation contract requires it. However, keep an independent correctness baseline so a faster candidate cannot succeed by reducing the workload, disabling assertions, or changing expected outputs solely to hide regressions.

Review whether tests would catch a realistic mistake, rather than evaluating quality through test count alone. Selective coverage inspection and mutation testing can expose gaps, but passing either does not prove correctness. For native or unsafe Rust, inspect actual proof obligations and validate the platforms that matter. See [risk-weighted verification](verification/assurance.md).

## A practical brief for an AI coding agent

Give an AI agent the issue, accepted design constraints, supported environments and a measurable definition of done. Ask it to:

- Explain the behavioral contract and the facts each consequential check must establish.
- Investigate realistic failure cases and expensive nested operations before adding new abstractions.
- Implement the smallest clear design that satisfies those requirements.
- Update tests where justified, and retain independent evidence that the expected behavior still holds.
- Run applicable formatting, linting, tests, and controlled performance comparisons.
- Report the exact commit, which checks actually ran, observed results and remaining limitations.

A human reviewer should evaluate the same evidence. A separate agent can explore different algorithms or independently review a candidate, but its output is not automatically authority to merge, release or change user-owned data.

## Get started

Use [the standards index](standards.md) for requirements, [the adoption guide](adoption.md) to choose a project scope, and [installable Rust skills](skills.md) to help agents locate the current rules. RCS favors **correct behavior, efficient execution, and readable code**, not more lines, more tests, more process, or simply more agent output.

For performance-sensitive applications, review [performance and execution cost](rules/performance.md). For high-risk operations, start with [unsafe and data safety](rules/safety.md), [error handling](rules/types-and-errors.md), and [behavioral verification](verification/assurance.md).
