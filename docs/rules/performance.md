# Performance and execution cost

The purpose is to catch **real, significant repeated work**, not to enforce numerical budgets or optimize small code prematurely.

## RCS-PERF-001 — Review work across call paths {#rcs-perf-001--review-work-across-call-paths}

**Level:** Required when the changed or invoked path reads large data, does expensive external work, repeats in a batch, or contains consequential latency.

**Enforcement:** Transitive call-path review, targeted instrumentation and representative synthetic measurements when useful.

Count actual expensive calls along the *entire action path*: an apparently harmless native file check may call helpers that each hash a multi-gigabyte source. Distinguish checks that prove a new safety fact from redundant scans of the same protected object.

Poor shape (illustrative pseudocode):

```rust
let first = inspect_entire_file(path)?;
let size = inspect_entire_file(path)?.byte_length();
let hash = inspect_entire_file(path)?.sha256();
```

Better *when the data is qualified for reuse within the same stable observation*:

```rust
let observed = inspect_entire_file(path)?;
let size = observed.byte_length();
let hash = observed.sha256();
```

In real code, `inspect_entire_file` is a project-owned helper; these snippets are schematic. **Do not cache mutable disk data across unrelated verification boundaries** or weaken source/target identity, concurrency or recovery invariants merely to avoid I/O.

For large sources, stream bytes through one bounded buffer and update all necessary digests and counters in a single pass where safe. Do not substitute an unbounded `fs::read` for streaming just to reduce call counts.

A useful finding documents: action → nested call chain → number of full passes or queries → size/frequency → effect on time/I/O → which checks are actually independent → smallest safe correction. The count is evidence, not a hard pass/fail quota.

## RCS-PERF-002 — Optimize with evidence {#rcs-perf-002--optimize-with-evidence}

**Level:** Advisory.

**Enforcement:** Review, profiles, measurements and regression tests if appropriate.

Prefer simple idiomatic code until a measurable or strongly bounded cost matters. Explain the baseline, proposed algorithm and safety tradeoff.

Before introducing concurrency, caching or elaborate adapters, ask whether it addresses the true bottleneck and what failure modes it adds. Benchmark with synthetic and controlled data; performance results from one machine do not imply identical throughput on HDDs, SSDs, USB drives and network mounts.

A larger cohesive function may be easier to review and faster than a deeply layered micro-abstraction. Neither line count nor "number of defensive checks" is itself a flaw.

[Back to standards index](../standards.md).
