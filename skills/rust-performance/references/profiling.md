<!-- SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix) -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# Profiling the limiting work

## Choose a measurement

| Question | Starting evidence |
| --- | --- |
| Which code consumes CPU? | Optimized, symbolized sampling profile |
| Why do more workers stop helping? | Thread timeline, blocked stacks, lock wait and lock hold intervals |
| Is storage or native metadata work dominant? | I/O events, native-call counts and durations tied to the operation |
| Are allocations or copies costly? | Allocation counts/stacks, retained heap and copy profiles |
| Is a pure function cheaper? | Criterion; instruction profiling on supported hosts |
| Is the binary or build too large/slow? | Cargo timings, feature inspection and size/codegen tools |

Read the installed tool's help and current documentation. Verify that its
version supports the required platform, events and symbol format. Start with
a bounded capture of the owned process and workload. Record missing stacks,
dropped events, sampling limitations and capture overhead.

On Windows, evaluate [samply](https://github.com/mstange/samply) for CPU and
blocked-thread stacks, or
[WPR/WPA](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/) for ETW
thread, CPU and I/O analysis. Select the required recording profile; not
every capture contains every event.

On Linux, evaluate perf or samply for CPU work and suitable scheduler/I/O
tracing for waiting. Do not infer that every profiler exposes off-CPU stacks
on every platform. On macOS, evaluate Instruments or samply. Use DHAT,
heaptrack or another allocation profiler only on supported platforms and
with its instrumentation/overhead accounted for.

Preserve matching debug information for optimized code. A flamegraph with
unresolved native frames cannot establish their Rust callers precisely.
Use an isolated profiling configuration rather than silently changing
shared Cargo configuration, compiler flags or machine-wide permissions.

## Interpret spans and concurrency

Wall time is the operation's elapsed duration. Summed thread CPU time is
work across threads, and may exceed wall time. Inclusive spans contain
children; exclusive spans exclude only children the instrumentation actually
accounts for. Verify the instrumentation model before subtracting totals.

Summed worker lock wait can exceed wall time because workers wait
simultaneously. Inclusive serialized-state time includes its nested SQL,
validation and native calls. Identify the critical path from timestamps and
thread relationships, then inspect the work holding up that path.

For example, a hypothetical 40-second batch with 90 seconds summed worker
wait and 30 seconds inclusive state work does not have 120 seconds to
remove. If COMMIT spans total one second, a proposal to save 29 seconds
through batching needs evidence of additional eliminated work. Timestamp
lock acquisition/release and attribute nested service time before estimating
a bound. Amdahl-style bounds need measured critical-path fractions, not
overlapping component sums.

## Capture scope and privacy

Inspect active recordings and owned resources before starting or stopping a
capture. Profiling can record other processes, paths, command lines and
symbols. Use approved local storage; review artifacts before any upload or
public example. Do not publish raw traces as part of reusable guidance.

## References

- [Rust Performance Book: profiling](https://nnethercote.github.io/perf-book/profiling.html)
- [samply capabilities and symbols](https://github.com/mstange/samply)
- [Windows Performance Recorder](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/windows-performance-recorder)
