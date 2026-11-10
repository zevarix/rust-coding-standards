<!-- SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix) -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# Selecting an optimization

## Find avoidable work before adding machinery

Trace the whole operation, including helpers called from apparently cheap
checks. Count passes, native opens, queries, serialization, copies and
allocations per input, output and batch. Examine complexity as both input
count and payload size grow; a small fixed fixture can hide quadratic work.

Prefer a simpler algorithm or fewer redundant passes when evidence supports
it. Reuse buffers or immutable observations within their proven lifetime.
Borrowing, clone avoidance, streaming and preallocation are options, not
automatic improvements. Measure real allocation sites and memory retention;
a small-vector container can increase object size or still spill to heap.

Keep product guarantees distinct from their implementation. Identify the
fact each validation establishes and whether another operation proves that
same fact within a stable ownership boundary. Reusing mutable filesystem or
database facts across unrelated boundaries needs an explicit validity
argument. Follow the consuming project's actual database ownership contract
rather than assuming outside applications can rewrite its live schema.

## Investigate serialization

For a worker pipeline, distinguish useful parallel work from time waiting
for admission, writer locks, persistence and completion. Measure lock hold
time and the nested work performed under the lock.

For SQLite, separate statement preparation, reads, transaction admission,
COMMIT, serialization, filesystem checks and application bookkeeping.
Batching can reduce transactions or repeated surrounding work, but one
number labeled database time does not establish which saving is available.

Consider connection lifetime, prepared-statement reuse, transaction shape,
queueing and backpressure only after checking what already exists. A
dedicated writer or more workers can add latency and recovery complexity.
Keep completion registration consistent with actual verified effects, and
preserve required Stop/Resume and error behavior.

## Treat compiler changes as separate experiments

Read [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)
and [rustc codegen options](https://doc.rust-lang.org/rustc/codegen-options/index.html)
for the actual supported toolchain. Evaluate LTO, codegen units, PGO,
inlining, allocator changes and SIMD against the measured bottleneck.

There is no universal speedup percentage. CPU-specific compilation changes
deployment compatibility; panic strategy changes failure behavior; stripping
symbols changes diagnosis. These are not a standard bundle to apply to
every release. Keep profiling and shipping configurations distinguishable.

## Decide what to retain

Change one cause so the result can be attributed. Prove the affected
correctness contracts with appropriate tests, then compare the representative
operation. Assess throughput/latency, memory, CPU, I/O, build and maintenance
costs. A local improvement may be hidden by another bottleneck or offset by a
regression elsewhere.

Retain measured small improvements and noisy/adverse observations in the
project's evidence. Make the retention decision explicit: demonstrated
workflow gain, proven reduction in work, justified simplification, exploratory
candidate or rejection. Passing correctness tests alone does not establish
a worthwhile optimization or override a previous rejection.

## Sources and authorship

This guidance is independently written and uses no copied third-party code
or prose. General workflow comparison included
[full-stack-skills/rust-skills: rust-performance](https://github.com/full-stack-skills/rust-skills/blob/b8a6af74af28ee86b8cbbbc3075cde0b31a5155e/skills/rust-performance/SKILL.md)
at commit `b8a6af74af28ee86b8cbbbc3075cde0b31a5155e`, skill blob
`6ca89c880285d39ecd9698f29609d43325879405`. That source declares Apache-2.0;
the original RCS wording remains MIT OR Apache-2.0 under this repository's
copyright notice.

Technical references: [Rust Performance Book](https://nnethercote.github.io/perf-book/),
[Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html),
[rustc codegen](https://doc.rust-lang.org/rustc/codegen-options/index.html)
and the profiling tools' own documentation. Verify version-sensitive details
when applying them; these links do not endorse a particular tool installation.
