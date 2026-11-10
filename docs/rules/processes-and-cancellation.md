# External processes and cancellation

External tools are outside Rust's type and memory-safety guarantees. These rules apply when a Rust application launches another program, consumes its output, or allows consequential work to be interrupted.

## RCS-PROC-001 — Qualify tools and use structured arguments {#rcs-proc-001--qualify-tools-and-use-structured-arguments}

**Level:** Required when launching external executables or passing untrusted paths/values as arguments.

**Enforcement:** Review executable selection and `Command` construction, test a synthetic fake executable's argv, and inspect version/capability failures.

### Requirement

Select an executable through the project's approved configured-path/PATH policy and establish the **required capability/version**, not just that a similarly named binary exists. Build arguments with `std::process::Command` and separate `arg`/`args`, never interpolate untrusted data into a shell command string. Preserve platform-native `Path`/`OsStr` values when passing filenames. Do not put tokens, passwords or private data in argv, command echo, error logs or serialized receipts when a safer private input channel is needed.

**Avoid** shell interpretation of user paths:

```rust
let command_line = format!("unzip -l {}", user_path.display());
std::process::Command::new("sh").args(["-c", &command_line]).output()?;
```

**Prefer** constructing arguments as distinct operating-system values; this self-contained test does **not** invoke a real tool:

<!-- rcs-example: test -->
```rust
use std::{ffi::OsStr, path::Path, process::Command};

pub fn list_archive_command(program: &Path, archive: &Path) -> Command {
    let mut command = Command::new(program);
    command.arg("list").arg("--").arg(archive);
    command
}

#[test]
fn path_with_spaces_is_one_argument() {
    let command = list_archive_command(
        Path::new("synthetic-inspector"),
        Path::new("invented collection/archive.zip"),
    );
    let args: Vec<&OsStr> = command.get_args().collect();
    assert_eq!(
        args,
        [
            OsStr::new("list"),
            OsStr::new("--"),
            OsStr::new("invented collection/archive.zip"),
        ]
    );
}
```

This proves argument separation only. Real tool flags and the meaning of `--` are **tool-specific** and must be qualified, not assumed. A program that accepts `--version` may still lack an operation the caller needs.

### Reviewer check

Trace configured executable identity, provider/version probe, actual command argv, environment, working directory and secrets into the child process. Test a missing, renamed, incompatible or maliciously shaped fake tool, path containing spaces/non-UTF-8 where supported, and a fake argv recorder. Verify that no shell interpolation or misleading "tool verified" status bypasses qualification.

**Exception:** A deliberately invoked shell script is an external integration in its own right. Its caller still has to control script identity, input quoting and trust boundaries; a blanket ban on all shells is not the purpose of this rule.

**Source:** [Rust `Command`](https://doc.rust-lang.org/std/process/struct.Command.html).

## RCS-PROC-002 — Verify process outcomes and bounded output {#rcs-proc-002--verify-process-outcomes-and-bounded-output}

**Level:** Required when process output becomes catalog data, a completed result, or any other consequential state.

**Enforcement:** Fake-executable tests of exit status, truncated/malformed output, timeouts, stderr, excessive output and process cleanup; application-level output verification.

### Requirement

A child exiting successfully does **not** prove its expected output is complete or correct. Handle spawn/exit/termination errors, bound untrusted stdout/stderr capture and parse results through the same untrusted-input rules as file data. For a long-lived process, design cancellation/timeout and child **wait/reap** so resource handles and any child effects are reconciled; avoid assuming dropping `Child` stops or waits for it.

**Avoid** treating status alone as success:

```rust
let output = command.output()?;
if output.status.success() {
    register_completed_file(destination)?;
}
```

**Prefer** the conceptual sequence below (application pseudocode; cancellation and file-output proof depend on the actual tool):

```text
qualified executable + structured argv
  -> spawn with bounded output handling and cancellation strategy
  -> collect exit/timeout/termination result; wait/reap child
  -> parse output; reject malformed or partial authoritative records
  -> verify required destination bytes/identity independently
  -> record completion only under the owning state contract
```

A caller may stream logs to an owned bounded sink or consume stdout incrementally rather than buffer it all in memory. Some tools report useful partial non-authoritative diagnostics on failure; preserve them as diagnostics without turning them into a successful result.

### Reviewer check

Test fake tools that return `0` with absent output, nonzero with plausible output, malformed records, long stderr, early pipe close and cancellation after work begins. Prove the caller neither hangs from pipe backpressure nor fabricates completion. Determine which output files or side effects may survive a killed process and how they are reconciled.

**Exception:** A short, read-only diagnostic command without persistent effects may have a simpler timeout and result contract than an archive writer.

**Sources:** [Rust `Child`](https://doc.rust-lang.org/std/process/struct.Child.html), [Rust `Output`](https://doc.rust-lang.org/std/process/struct.Output.html).

## RCS-CANCEL-001 — Separate stop requests from durable effect truth {#rcs-cancel-001--separate-stop-requests-from-durable-effect-truth}

**Level:** Required when interruption, cancellation or restart can overlap a consequential file, database or external-tool operation.

**Enforcement:** Tests at pre-effect, mid-effect, post-effect/pre-acknowledgment and restart boundaries; inspection of retained receipts and actual effects.

### Requirement

Treat "pause requested", "process stopped" and "effect rolled back" as **different observations**. A cooperative stop generally means do not start more work, not that an in-flight write vanished. On restart, inspect current durable/physical evidence before retrying effects whose completion is uncertain. Preserve atomic publication, explicit receipt ownership, and source/user-data invariants. This complements [RCS-STATE-002](mutable-effects.md#rcs-state-002--reconcile-uncertain-effects-before-retrying-them).

**Avoid** manufacturing a clean retry simply because cancellation was requested:

```rust
if cancellation_requested {
    mark_effect_not_started()?;
    retry_copy()?;
}
```

**Prefer** an explicit outcome after a trustworthy physical/state reconciliation (this code models **decisions**, not how the observations are proven):

<!-- rcs-example: test -->
```rust
#[derive(Debug, Eq, PartialEq)]
pub enum ResumeDecision {
    AlreadyVerified,
    SafeToStart,
    NeedsReconciliation,
}

#[derive(Debug, Eq, PartialEq)]
pub enum EffectEvidence {
    CurrentVerifiedReceipt,
    ConfirmedAbsent,
    Uncertain,
}

pub fn decide_resume(evidence: EffectEvidence) -> ResumeDecision {
    match evidence {
        EffectEvidence::CurrentVerifiedReceipt => ResumeDecision::AlreadyVerified,
        EffectEvidence::ConfirmedAbsent => ResumeDecision::SafeToStart,
        EffectEvidence::Uncertain => ResumeDecision::NeedsReconciliation,
    }
}

#[test]
fn uncertainty_never_authorizes_a_replay() {
    assert_eq!(decide_resume(EffectEvidence::Uncertain),
               ResumeDecision::NeedsReconciliation);
    assert_eq!(decide_resume(EffectEvidence::ConfirmedAbsent),
               ResumeDecision::SafeToStart);
}
```

Only a current qualified verifier can produce those `EffectEvidence` cases in real code; passing an arbitrary caller-supplied enum is not evidence. A "safe to start" decision remains subject to current approval, target identity and collision checks.

### Reviewer check

List the effect boundaries around which cancellation can arrive and the durable state observable after restart. Inject interruption in synthetic fixtures, verify no false completion, no unverified duplicate work and no source deletion. Distinguish cooperative cancellation, force termination, panics, machine crash and provider timeout where the implementation actually supports them.

**Exception:** Pure in-memory operations without external effects may stop immediately without recovery machinery. Repeating an operation proven idempotent can also be safe under its documented conditions.

[Back to standards index](../standards.md).
