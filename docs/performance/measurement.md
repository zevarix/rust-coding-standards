<!-- SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix) -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# Comparable measurement

## Define the experiment

Record the user-visible operation, workload identity and scale, input format
mix, output criteria, concurrency, platform, toolchain, features and metric.
Keep preparation, timed execution and output inspection distinct. A narrowly
scoped microbenchmark answers a local question; retain a whole-operation
measurement for application claims.

Use actual representative data under the consuming project's permissions.
For public examples use independently generated or redistributable inputs;
a synthetic example does not establish performance on a private collection.
Record whether caches are warm, cold or uncontrolled. Never label a run
cold merely because it is the first invocation.

## Prove what ran

Bind each execution to the source revision/tree, dirty state, dependency
resolution, target, features, compiler and optimized profile. Identify the
actual executable by path and cryptographic hash. Read embedded provenance
when available, or retain an equivalent build-to-artifact receipt. A shared
target directory's newest executable is not evidence of its source.

Freeze known artifacts or use isolated build outputs when revisions could
collide. Keep symbols matched to the profiled artifact. Do not compare a
profiling build with a normal build as if only the source changed.

## Preserve comparable state

Inspect saved reports and uncertain submitted effects before retrying.
When execution changes files, a database, receipts or a saved plan, use new
owned output roots and equivalent newly prepared state. Preserve completed
and failed evidence. Do not reset a finished plan to manufacture a repeat.
Pure operations with no persistent effects can reuse immutable inputs.

Prevent competing builds, packaging and analysis from contaminating timed
work. Record external load or power/thermal conditions that could explain a
difference. Keep required progress and correctness behavior comparable.

Run diagnostic captures separately from canonical timing when their
overhead is material. Measure that overhead with a matched comparison if it
affects interpretation; do not silently compare diagnostics-on with
diagnostics-off.

## Compare and report

Use matched repetitions and alternate or randomize baseline/candidate order
when practical. Choose sample count for the observed variability and effect
size; do not impose a universal repetition count or percentage threshold.
Retain individual samples, failures, absolute differences and relative
differences with a clearly named denominator.

A single pair supports an observed difference, not statistical significance
or a general speedup. Report spread and uncertainty honestly; calculate
confidence intervals only when the sampling method supports them. Inspect
small, neutral and adverse results instead of discarding inconvenient runs.

Verify the same outputs and required recovery outcomes before accepting a
performance conclusion. Report memory, CPU, I/O and build-cost regressions
where relevant. Distinguish fewer expensive operations from a demonstrated
elapsed-time benefit.

## References

- [Criterion measurement analysis](https://bheisler.github.io/criterion.rs/book/analysis.html)
- [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)
- [Rust Performance Book: benchmarking](https://nnethercote.github.io/perf-book/benchmarking.html)
