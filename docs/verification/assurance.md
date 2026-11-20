---
title: "Rust Verification: Behavioral Tests and Unsafe Code"
description: "Assess Rust behavior using positive and negative tests, targeted mutation analysis, and appropriate unsafe-code checks without arbitrary coverage quotas."
tags:
  - Testing
  - Safety
  - AI-assisted Development
---

<!-- SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix) -->
<!-- SPDX-License-Identifier: MIT OR Apache-2.0 -->

# Risk-weighted behavioral verification

Use this method when the cost of an incorrect Rust result justifies more than
ordinary happy-path testing. It applies to human- or AI-authored code. The
owning project determines its guarantees, supported platforms and review
authority; [RCS-TEST-004](../rules/testing.md#rcs-test-004--verify-consequential-behavior-not-only-execution)
is advisory. Do not turn this workflow into a universal CI checklist.

## 1. Identify the claim and its failure cost

State what the component must do, what it must never claim, and which inputs
or states are realistic. Separate:

- **Reversible low-risk work:** ordinary tests and review may be enough.
- **Consequential decisions:** APIs, compatibility detection, parsing,
  authorization and durable state need evidence against false acceptance and,
  when applicable, false rejection of valid cases.
- **Unsafe/native boundaries:** trace actual safety invariants and caller
  obligations, then use additional tools and target-specific tests where supported.

Write down the load-bearing types, current ownership, state transitions,
supported platforms and accepted assumptions before implementation. Assume
ordinary failures are possible; do not invent unreachable emergencies to
inflate test counts.

## 2. Test the behavioral structure

For a finite state machine, identify meaningful states, allowed and rejected
transitions, and any irreversible effects. Test success and failure at the
important boundaries using deterministic, owned fixtures. For workflows
with real external effects, separately test current identities, durable
completion, interruption and replay as required by the owning project.

This small example tests a transition model. It **does not** establish that
any actual output was written, verified or persisted.

<!-- rcs-example: test -->
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Status {
    Planned,
    Staged,
    Verified,
}

#[derive(Clone, Copy)]
enum Event {
    Stage,
    Verify(bool),
}

fn advance(status: Status, event: Event) -> Result<Status, &'static str> {
    match (status, event) {
        (Status::Planned, Event::Stage) => Ok(Status::Staged),
        (Status::Staged, Event::Verify(true)) => Ok(Status::Verified),
        (Status::Staged, Event::Verify(false)) => Err("mismatch"),
        _ => Err("invalid transition"),
    }
}

#[test]
fn verifies_valid_and_rejected_transitions() {
    assert_eq!(advance(Status::Planned, Event::Stage), Ok(Status::Staged));
    assert_eq!(advance(Status::Planned, Event::Verify(true)), Err("invalid transition"));
    assert_eq!(advance(Status::Staged, Event::Verify(false)), Err("mismatch"));
    assert_eq!(advance(Status::Staged, Event::Verify(true)), Ok(Status::Verified));
    assert_eq!(advance(Status::Verified, Event::Stage), Err("invalid transition"));
}
```

When interleaving matters, deterministic barriers or an appropriate simulation
harness can test critical orderings. Do not mistake a model's green test for
proof about untested operating-system operations, crash durability or FFI.

## 3. Inspect coverage, then test the tests

A supported coverage tool (for example, `cargo-llvm-cov`) can identify untested
branches on the **relevant logic**. Coverage is execution evidence, not proof
that tests assert the intended outcome. Inspect both the covered cases and
what they observe.

For meaningful consequential logic, consider running a bounded
`cargo-mutants` experiment against the smallest applicable crate, module or
function. Check the installed tool's current documentation for supported
selection and test commands. Investigate each important surviving mutant:
does it change an observable contract, is it equivalent or out of scope,
or did a timeout, flaky test or unsupported build prevent evaluation?
Add an assertion or test only where the survivor exposes a real gap.

There is no universal coverage percentage, mutation score or required
sample count. Record missing tool support and any untested logic honestly.

## 4. Exercise unsafe boundaries where supported

For `unsafe` Rust, review each actual precondition and how callers establish
it. Consider Miri on eligible self-contained tests and sanitizers such as
ASan on instrumented, supported configurations. Miri cannot validate
arbitrary platform FFI, and sanitizers only observe paths and targets they
can instrument. Neither replaces careful proof-oriented review or native
platform acceptance. Use the [unsafe rule](../rules/safety.md#rcs-safe-001--justify-unsafe-operations)
and verify current toolchain/target documentation before running commands.

## 5. Report what is proved

State the reviewed source revision and affected contract; describe executed
tests, tool versions/configurations and their results, supported platforms,
important surviving mutations or uncovered paths, and what remains
unverified. Separate synthetic/model results from actual external effects.
A successful check does not independently grant merge or release authority.

### A compact brief for an AI coding agent

Give an agent a task-specific brief with:

- **Design:** inputs, outputs, load-bearing types, invariants and state changes.
- **Constraints:** project rules, valid assumptions, unsupported or unsafe
  operations, and the actual risk boundary.
- **Verification:** named positive and realistic negative cases; any targeted
  coverage/mutation or unsafe tools worth using; accepted evidence and known
  limitations.
- **Done means:** exact code revision, verified behavior, reviewable diff,
  performed checks and candid remaining risks.

The agent should propose a simple design and run only supported, relevant
checks. Humans and agents both remain responsible for the correctness of
their review claims. For performance work, use the existing
[measurement guide](../performance/measurement.md), not a separate
benchmark protocol.

## References

- [JetBrains interview on AI for Rust development (2026)](https://blog.jetbrains.com/rust/2026/11/04/ai-for-rust-development/)
- [cargo-mutants](https://mutants.rs/)
- [cargo-llvm-cov](https://github.com/taiki-e/cargo-llvm-cov)
- [Miri](https://github.com/rust-lang/miri)
- [Rust compiler sanitizer options](https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html)

The workflow, examples and descriptions here are original RCS guidance,
not redistributed text or code from these sources.
