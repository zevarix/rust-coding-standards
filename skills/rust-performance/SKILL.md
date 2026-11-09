---
name: rust-performance
description: Use when Rust code is slow, performance changes need comparison, worker scaling stalls, or CPU, allocation, memory, I/O, binary-size or build-time costs need investigation.
---

<!-- SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix) -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# Rust performance

Investigate the user-visible operation through its complete call path. Choose
the simplest change that addresses an evidenced cost and preserves the
consuming project's correctness contract.

## Establish the task

Read the consuming repository's instructions, owning work item and applicable
[RCS rules](https://github.com/zevarix/rust-coding-standards/blob/main/docs/standards.md).
Resolve the project's chosen RCS reference to an actual commit and read the
linked documentation at that revision. Use an authorized GitHub read route
or an existing checkout; report any unavailable pages. The links below
locate canonical documentation rather than a bundled rulebook.
Record the actual revisions inspected. Keep architecture, safety, supported
platforms and merge/deployment authority with that project. An audit request
authorizes investigation; it does not authorize implementation, installation
or a benchmark that mutates user data.

Identify the operation, input scale, success metric and required outcomes.
Separate initial work from recovery, startup from steady state, and workload
time from preparation or post-run inspection.

## Investigate and compare

1. **Establish comparable evidence.** Read existing completed and failed
   results before scheduling work. Prove the executed artifact's source and
   optimized configuration. Select representative inputs and equivalent
   starting state. Read [measurement](https://github.com/zevarix/rust-coding-standards/blob/main/docs/performance/measurement.md) before a
   baseline, comparison or performance claim.
2. **Locate the limiting work.** Trace orchestration, workers, locks,
   persistence, native calls and output verification. Count expensive nested
   operations per item and per batch. Distinguish on-CPU work, blocked time,
   I/O and instrumentation overhead. Read
   [profiling](https://github.com/zevarix/rust-coding-standards/blob/main/docs/performance/profiling.md) to select a platform-appropriate
   measurement.
3. **Form a falsifiable hypothesis.** State the call path, frequency, observed
   cost, reuse boundary, proposed mechanism and result that would reject it.
   Separate confirmed costs from plausible causes. Read
   [optimization](https://github.com/zevarix/rust-coding-standards/blob/main/docs/performance/optimization.md) when selecting an experiment.
   Identify behavior changes explicitly; a faster operation with different
   integrity or recovery guarantees is a different contract.
4. **Change and qualify one cause.** Within authorized implementation scope,
   preserve required behavior and use targeted tests plus a representative
   whole-operation comparison. Keep builds and heavy analysis outside timed
   runs. Record resource and maintenance tradeoffs as well as elapsed time.

## Interpret the evidence

Inclusive spans contain child work. Worker intervals and summed lock waits
can overlap; they are not additive wall time or a promise of removable
latency. A local benchmark improvement does not establish an application
improvement. Report a single comparison as an observation with uncertainty.

Retain small, neutral and adverse observations. A proven reduction in calls,
allocation or complexity can be useful even when elapsed-time evidence is
noisy; label those separate findings and apply the project's retention
criteria. Do not invent a speedup or declare an unmeasured target impossible.

## Report

Present: artifact and workload provenance; baseline and candidate protocol;
raw-result location and sample counts; absolute and relative observations;
profile interpretation; correctness evidence; secondary costs; limitations;
and the next experiment or retention decision.

For each proposed optimization, give the source path/symbol, evidence,
expected mechanism, uncertainty and smallest experiment. Publish only
sanitized summaries and redistributable examples; keep raw project data,
profiles and machine details in the consuming project's approved location.
