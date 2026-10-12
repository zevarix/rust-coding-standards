# Progress, diagnostics and logging

Long-running work is not automatically a performance defect. A correct operation may
need to hash large files, inspect many entries, wait for an external tool, reconcile a
database, or finalize durable state. When that work is exposed to people or automation,
the software should make useful progress observable without confusing presentation with
proof that an effect completed.

These rules deliberately separate three concerns:

- **progress/status** answers what the operation is doing now;
- **verbose diagnostics** provide opt-in deeper live detail when that is useful;
- **logs** preserve or export diagnostic evidence for later investigation.

An adopting project still owns its CLI/UI contract, privacy model, logging destination,
retention policy, and authoritative completion state.

## RCS-PROGRESS-001 — Keep perceptibly long operations observable {#rcs-progress-001--keep-perceptibly-long-operations-observable}

**Level:** Required when a user-facing or automation-facing operation can take long enough,
or vary enough in duration, that silence can reasonably resemble a hang.

**Enforcement:** Review operation/event boundaries and presentation channels; exercise
determinate, indeterminate, finalization, non-interactive and structured-output paths with
synthetic work. Measure update overhead when progress itself can become frequent.

### Requirement

Expose useful liveness while the work is actually in progress. Do **not** impose a
universal threshold such as "anything over two seconds": whether progress is warranted
depends on the workload, interface and user expectation.

For determinate work, prefer meaningful units the operation already knows, such as
items, bytes or stages completed and the total when reliable. Elapsed time is generally
useful; throughput and ETA are useful only when they are stable enough not to mislead.
For work whose total is not knowable, expose a phase or liveness indication instead of
inventing a percentage.

Report finalization, cleanup, indexing, durable publication or similar post-work phases
when they can take noticeable time. Do not display `100%` and then remain silent while a
material final phase continues.

Keep the default presentation concise. When the application has materially useful deeper
live diagnostics, provide an opt-in verbosity control at the presentation boundary
(for a CLI, `--verbose` is a conventional choice). Verbose output may include individual
items, subprocess phases, retry decisions, cache decisions or validation steps, but it
must remain bounded and must follow the same secret/private-data rules as logs. Do not
manufacture verbose output for trivial operations merely to satisfy this rule.

Application/core code should expose typed phase/progress observations or an equivalent
event interface; a CLI, GUI or other presentation layer decides whether those become a
spinner, progress bar, compact line, notification or verbose text. Interactive TTY output
may update in place. Non-interactive/automation paths should receive deterministic
progress or phase events when the owning interface contract calls for them.

Machine-readable stdout must remain valid. A JSON/NDJSON or other structured-output mode
must not be contaminated with human spinner/progress/verbose text. Use the project's
defined structured event channel, stderr/diagnostic channel, or another documented
separation.

Throttle or coalesce high-frequency updates so progress reporting does not become the hot
path. Reporting every byte, record or inner-loop iteration is usually worse than reporting
meaningful changes at a bounded cadence.

Progress is **observability, not completion evidence**. A rendered `100%`, "finished"
event, or final progress update must never substitute for the verification, durability,
state-transition or reconciliation proof required by the owning application.

### Example: core emits progress; presentation decides rendering

<!-- rcs-example: test -->
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Phase {
    Scanning,
    Hashing,
    Finalizing,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Progress {
    pub phase: Phase,
    pub completed: u64,
    pub total: Option<u64>,
}

pub trait ProgressSink {
    fn report(&mut self, progress: Progress);
}

impl ProgressSink for Vec<Progress> {
    fn report(&mut self, progress: Progress) {
        self.push(progress);
    }
}

pub fn process_three_items(sink: &mut impl ProgressSink) {
    for completed in 1..=3 {
        sink.report(Progress {
            phase: Phase::Hashing,
            completed,
            total: Some(3),
        });
    }
    sink.report(Progress {
        phase: Phase::Finalizing,
        completed: 3,
        total: Some(3),
    });
}

#[test]
fn finalization_is_visible_after_determinate_work() {
    let mut events: Vec<Progress> = Vec::new();

    process_three_items(&mut events);

    assert_eq!(events.last().unwrap().phase, Phase::Finalizing);
}
```

The example proves separation between operation events and rendering only. A production
application still decides update cadence, cancellation behavior, output channels and what
constitutes verified completion.

### Reviewer check

- Identify operations whose normal or worst-case duration can plausibly leave a person or
  automation waiting without feedback.
- Check that reported units correspond to real work and that an unknown total remains
  indeterminate rather than a fabricated percentage.
- Inspect the transition into finalization/cleanup so the UI does not appear frozen after
  the main counter reaches its total.
- Verify structured stdout remains contract-valid in progress and verbose modes.
- Look for progress callbacks inside tight loops and bound their update frequency/cost.
- Confirm verbose mode, when useful, is opt-in and does not leak secrets/private payloads.
- Confirm progress state cannot be mistaken for durable or authoritative completion.

**Exceptions:** Effectively instantaneous operations do not need progress UI. A pure
library with no user-facing lifecycle may expose useful events/callbacks/results to its
caller rather than rendering anything itself.

**Related:** [RCS-PERF-001](performance.md#rcs-perf-001--review-work-across-call-paths),
[RCS-PERF-002](performance.md#rcs-perf-002--optimize-with-evidence), and
[RCS-CANCEL-001](processes-and-cancellation.md#rcs-cancel-001--separate-stop-requests-from-durable-effect-truth).

## RCS-TERM-001 — Keep terminal presentation recoverable and adaptable {#rcs-term-001--keep-terminal-presentation-recoverable-and-adaptable}

**Level:** Required when an application uses terminal control sequences, cursor hiding,
in-place animation, alternate screens, color-dependent status, or similar terminal state
for user-facing operation feedback.

**Enforcement:** Exercise TTY and non-TTY rendering paths, success/failure/cancellation
cleanup, plain-output mode, and representative narrow/redirected terminals. Review
terminal-state ownership and cleanup for early returns and panics where the project
supports panic recovery.

### Requirement

Treat terminal state as a resource that must be restored. If the application hides the
cursor, changes terminal modes, enters an alternate screen, or applies persistent styling,
pair acquisition with cleanup that runs on normal completion and ordinary error/cancel
paths. Prefer an RAII-style guard or another single ownership mechanism over scattered
"restore" calls that can be skipped by an early return.

A best-effort cleanup failure should not erase the operation's primary error. If restoring
terminal state itself can fail, retain the primary failure and surface cleanup trouble
through an appropriate diagnostic channel.

Do not emit terminal-control escape sequences merely because stdout/stderr exists. Detect
whether the selected presentation stream is an interactive terminal and fall back to plain,
deterministic text when output is redirected, piped, captured by tests, or otherwise
non-interactive. Machine-readable modes remain subject to
[RCS-PROGRESS-001](#rcs-progress-001--keep-perceptibly-long-operations-observable): human
terminal control must not contaminate their contract.

Provide a practical way to disable animation or in-place rendering when those effects are
material to the interface. This may be an explicit plain/no-animation option, an adopting
project's accessibility setting, or another documented mechanism. Do not require a
particular environment variable or terminal crate universally.

Do not encode essential state in color, animation, cursor position, spinner glyphs, or
other decoration alone. A user who disables styling, uses a screen reader, redirects
output, or views a retained log should still be able to determine the phase and final
outcome from text/structured state.

Choose rendering that degrades sensibly on constrained terminals. Compact output may
collapse detail while verbose mode exposes more, but neither should corrupt the terminal,
wrap an unbounded status line indefinitely, or hide the final result after animation ends.

Terminal rendering is presentation, not operation truth. Losing a TTY, failing to draw a
spinner, or switching to plain output must not change the underlying verification,
cancellation, persistence or recovery semantics.

### Example: choose an interactive renderer without changing operation semantics

<!-- rcs-example: test -->
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Presentation {
    Interactive,
    Plain,
}

pub fn presentation(is_terminal: bool, plain_requested: bool) -> Presentation {
    if is_terminal && !plain_requested {
        Presentation::Interactive
    } else {
        Presentation::Plain
    }
}

#[test]
fn redirected_or_explicit_plain_output_never_uses_terminal_animation() {
    assert_eq!(presentation(false, false), Presentation::Plain);
    assert_eq!(presentation(true, true), Presentation::Plain);
    assert_eq!(presentation(true, false), Presentation::Interactive);
}
```

This example models the presentation decision only. Real terminal code should use the
platform/runtime's actual terminal detection (for example Rust's standard terminal
detection where appropriate) and should own any terminal-state restoration with a guard
whose cleanup does not panic.

### Reviewer check

- Identify every terminal state changed by the interactive renderer and the single owner
  responsible for restoring it.
- Exercise normal success, recoverable error and cancellation/early-return paths; verify
  the cursor/mode/style is not left altered.
- Redirect/capture the selected output stream and verify no spinner, cursor-control or ANSI
  escape sequence leaks into plain/machine-readable output.
- Confirm users can obtain a non-animated/plain presentation when animation is materially
  used.
- Read output without color/animation and confirm phase, failure and final result remain
  understandable.
- Inspect high-frequency redraws for flicker, unnecessary work and unbounded line growth.
- Confirm terminal-rendering failure cannot fabricate operation failure/success or bypass
  the application's actual state transitions.

**Exceptions:** An application that emits only ordinary newline-delimited text and never
owns terminal state does not need terminal cleanup machinery. A full-screen terminal UI
may have a richer renderer contract, but it still needs deterministic state restoration,
noninteractive separation where supported, and an accessible way to recover essential
status without relying solely on decoration.

**Related:** [RCS-PROGRESS-001](#rcs-progress-001--keep-perceptibly-long-operations-observable),
[RCS-LOG-001](#rcs-log-001--emit-useful-bounded-and-safe-diagnostic-logs), and
[RCS-CANCEL-001](processes-and-cancellation.md#rcs-cancel-001--separate-stop-requests-from-durable-effect-truth).

## RCS-LOG-001 — Emit useful, bounded and safe diagnostic logs {#rcs-log-001--emit-useful-bounded-and-safe-diagnostic-logs}

**Level:** Required when an application owns long-running, multi-stage, external-effect or
recovery-sensitive workflows for which post-failure diagnosis materially matters. A
library may instead expose structured diagnostic events/errors to its caller.

**Enforcement:** Review logging/event call sites, levels, fields, error propagation,
redaction/privacy boundaries and configured sinks; test representative failure paths and
capture/suppression behavior. Inspect persistent-log rotation/retention when the
application owns a file or database sink.

### Requirement

Use diagnostic logs to help explain **what happened after the fact**: phase transitions,
retries, consequential failures, external-process boundaries, meaningful timing, recovery
decisions, and other context that would materially help debugging or support.

Prefer consistent severity semantics such as `error`, `warn`, `info`, `debug` and `trace`
(or a project-defined equivalent). Do not put ordinary per-item chatter at a severity that
makes default logs unusable.

Prefer structured/typed context where useful—such as operation or stage identity,
component, item/byte counts, elapsed time and outcome—rather than forcing every consumer
to parse prose. Preserve the useful error chain/cause at boundaries instead of reducing a
failure to "operation failed".

Never log credentials, tokens, private keys, authentication headers, secret configuration
or raw sensitive payloads. Avoid logging full user paths, filenames or other private
content when a stable operation/source ID, digest, relative label or redacted value is
sufficient for diagnosis. The adopting project defines any stricter privacy classification.

Logging must be bounded. Avoid one record per byte/inner-loop iteration and other shapes
that can create unbounded diagnostic volume or materially slow the operation. When the
application owns persistent logs, use project-appropriate rotation/retention or another
bounded lifecycle rather than assuming disk is infinite.

A failure to write an ordinary diagnostic log should normally not fail the product
operation. An **audit log, durable receipt or compliance record** is different: if the
application makes that record part of correctness, model and verify it as authoritative
state under the project's effect/recovery contract rather than pretending it is an
ordinary best-effort log.

Logs are **diagnostic evidence, not canonical state**. "Copied successfully" in a log is
not proof that bytes were verified, a transaction committed, a child was reaped, or a
durable manifest exists.

Keep machine-readable output separate from human logging. Tests should be able to capture,
redirect or suppress diagnostics without relying on brittle assertions over unrelated
stdout text.

Progress, verbose output and logs may share the same typed event source, but their
presentation and retention semantics remain distinct: a compact spinner is not a log,
verbose output is not necessarily retained, and a persisted log is not a completion
receipt.

### Example: diagnostic fields instead of secret-bearing prose

Avoid constructing a log message from an entire credential-bearing request:

```rust
// Do not do this when request can contain tokens or private payloads.
// eprintln!("upload failed: request={request:?} error={error}");
```

Prefer a small diagnostic value containing only context approved for logging:

<!-- rcs-example: test -->
```rust
#[derive(Debug, Eq, PartialEq)]
pub struct Diagnostic<'a> {
    pub operation_id: &'a str,
    pub stage: &'a str,
    pub elapsed_ms: u64,
    pub outcome: &'a str,
}

pub fn failed_upload(
    operation_id: &str,
    elapsed_ms: u64,
) -> Diagnostic<'_> {
    Diagnostic {
        operation_id,
        stage: "publish",
        elapsed_ms,
        outcome: "failed",
    }
}

#[test]
fn diagnostic_contains_operational_context_without_a_secret_field() {
    assert_eq!(
        failed_upload("op-17", 420),
        Diagnostic {
            operation_id: "op-17",
            stage: "publish",
            elapsed_ms: 420,
            outcome: "failed",
        }
    );
}
```

The example demonstrates field selection only. Production code still needs its chosen
logging/event framework, error chain, privacy policy, sink and retention behavior.

### Reviewer check

- Identify what evidence would be needed to diagnose a representative failure after the
  operation has ended.
- Check levels and fields for useful phase/timing/error context without repetitive noise.
- Trace secrets/private data into diagnostic formatting, including `Debug` dumps and
  wrapped external errors.
- Estimate log volume on large batches and failure/retry loops; verify bounded retention
  when the application owns persistent logs.
- Confirm ordinary logging failure is not accidentally a correctness dependency.
- Conversely, if a record is correctness-critical, ensure it is modeled under the
  application's durable-state/effect rules rather than as best-effort logging.
- Verify JSON/NDJSON stdout and tests are not coupled to incidental human log text.
- Confirm logs support diagnosis/performance investigation without being treated as
  authoritative completion state.

**Exceptions:** Small pure libraries and effectively instantaneous operations do not need
to create a persistent logging subsystem. They should still return actionable errors and
may expose structured diagnostic events when callers need them. An application that uses
an external tracing/logging service may satisfy the sink/retention aspects there, subject
to the same privacy, boundedness and authority distinctions.

**Related:** [RCS-ERR-002](types-and-errors.md#rcs-err-002--preserve-actionable-boundary-context),
[RCS-PROC-002](processes-and-cancellation.md#rcs-proc-002--verify-process-outcomes-and-bounded-output),
[RCS-STATE-001](mutable-effects.md#rcs-state-001--do-not-register-an-effect-as-complete-before-verification),
and [RCS-PERF-001](performance.md#rcs-perf-001--review-work-across-call-paths).

[Back to standards index](../standards.md).
