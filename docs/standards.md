# Rust Coding Standards — Working draft

These are **proposed shared rules**, not automatically accepted policy for every Zevarix repository. A project may explicitly adopt the **latest `main`** guidance without maintaining a commit pin, or choose a fixed revision for a specific assurance need. It retains its own scope, exceptions and stronger local rules. Code that predates adoption is not automatically noncompliant.

## Rule levels

- **Required:** the default expectation *within an adopting project's declared scope*. Deviations need a locally documented technical reason, not permission from this repository.
- **Advisory:** a preferred design or review question. Departures may be sensible and are not automatic review failures.

For either level, reviewers report demonstrated problems with a concrete call path, trigger and impact. A rule name by itself is not proof of a defect. Tool errors block only the affected validation claim or operation; they do not end unrelated safe progress.

Rule IDs use the prefix `RCS` for **Rust Coding Standards**. The rest of each ID identifies the subject and individual rule.

## Index

| Rule | Level | Enforced by | Concern |
| --- | --- | --- | --- |
| [RCS-FMT-001](rules/style-and-structure.md#rcs-fmt-001--format-with-rustfmt) | Required | `rustfmt` | Consistent Rust formatting |
| [RCS-NAME-001](rules/style-and-structure.md#rcs-name-001--use-idiomatic-names) | Required | Compiler/Clippy + review | Naming conventions |
| [RCS-MOD-001](rules/style-and-structure.md#rcs-mod-001--organize-by-responsibility) | Advisory | Human review | Cohesive modules, not line quotas |
| [RCS-META-001](rules/style-and-structure.md#rcs-meta-001--derive-package-release-versions-from-their-authority) | Advisory | Review/tests | Use package release metadata, not duplicate version literals |
| [RCS-TYPE-001](rules/types-and-errors.md#rcs-type-001--model-consequential-identities-distinctly) | Required* | Review/tests | Prevent identity/unit mixups |
| [RCS-NUM-001](rules/numbers-and-bounds.md#rcs-num-001--check-consequential-arithmetic) | Required* | Review/tests | Checked sizes, offsets and budgets |
| [RCS-NUM-002](rules/numbers-and-bounds.md#rcs-num-002--reject-lossy-conversions-where-identity-or-size-matters) | Required* | Review/tests | Explicit fallible narrowing |
| [RCS-INPUT-001](rules/untrusted-input.md#rcs-input-001--bound-actual-work-not-just-declared-sizes) | Required* | Review/tests | Bound actual untrusted decode work |
| [RCS-INPUT-002](rules/untrusted-input.md#rcs-input-002--make-malformed-or-partial-input-outcomes-explicit) | Required* | Review/tests | Reject incomplete authoritative parsing |
| [RCS-API-001](rules/types-and-errors.md#rcs-api-001--follow-predictable-api-conventions) | Advisory | Review/Clippy | Conventional Rust APIs |
| [RCS-ERR-001](rules/types-and-errors.md#rcs-err-001--use-explicit-recoverable-errors) | Required | Review/Clippy/tests | `Result` and error propagation |
| [RCS-ERR-002](rules/types-and-errors.md#rcs-err-002--preserve-actionable-boundary-context) | Advisory | Human review/tests | Diagnostic boundaries |
| [RCS-PROC-001](rules/processes-and-cancellation.md#rcs-proc-001--qualify-tools-and-use-structured-arguments) | Required* | Review/fake tools | Qualified structured process argv |
| [RCS-PROC-002](rules/processes-and-cancellation.md#rcs-proc-002--verify-process-outcomes-and-bounded-output) | Required* | Review/fake tools | Verify bounded process outcomes |
| [RCS-SAFE-001](rules/safety.md#rcs-safe-001--justify-unsafe-operations) | Required* | Review/tests | `unsafe` soundness |
| [RCS-DATA-001](rules/safety.md#rcs-data-001--protect-user-owned-data) | Required* | Review/tests | Non-destructive defaults |
| [RCS-FS-001](rules/mutable-effects.md#rcs-fs-001--recheck-mutable-filesystem-targets-before-consequential-effects) | Required* | Review/tests | Current file/target identity at effects |
| [RCS-PATH-001](rules/persistence-and-paths.md#rcs-path-001--do-not-confuse-pathname-text-with-filesystem-identity) | Required* | Review/tests | Native path representation vs physical identity |
| [RCS-DB-001](rules/persistence-and-paths.md#rcs-db-001--commit-related-state-transitions-atomically) | Required* | Review/tests | Atomic guarded SQLite transitions |
| [RCS-DB-002](rules/persistence-and-paths.md#rcs-db-002--qualify-the-live-schema-and-recovery-invariants) | Required* | Review/tests | Validate live SQLite enforcement schema |
| [RCS-STATE-001](rules/mutable-effects.md#rcs-state-001--do-not-register-an-effect-as-complete-before-verification) | Required* | Review/tests | Prove output before completion |
| [RCS-STATE-002](rules/mutable-effects.md#rcs-state-002--reconcile-uncertain-effects-before-retrying-them) | Required* | Review/tests | Reconcile ambiguous retry outcomes |
| [RCS-CANCEL-001](rules/processes-and-cancellation.md#rcs-cancel-001--separate-stop-requests-from-durable-effect-truth) | Required* | Review/tests | Stop requests versus effect truth |
| [RCS-CONC-001](rules/concurrency-and-tooling.md#rcs-conc-001--make-shared-state-invariants-atomic-at-the-right-boundary) | Required* | Review/contended tests | Atomic shared-state admission |
| [RCS-PERF-001](rules/performance.md#rcs-perf-001--review-work-across-call-paths) | Required* | Review/instrumentation | Avoid costly duplicate work |
| [RCS-PERF-002](rules/performance.md#rcs-perf-002--optimize-with-evidence) | Advisory | Profiling/review | Avoid premature optimization |
| [RCS-PROGRESS-001](rules/observability.md#rcs-progress-001--keep-perceptibly-long-operations-observable) | Required* | Review/tests | Observable long-running work |
| [RCS-TERM-001](rules/observability.md#rcs-term-001--keep-terminal-presentation-recoverable-and-adaptable) | Required* | Review/tests | Recoverable terminal presentation |
| [RCS-LOG-001](rules/observability.md#rcs-log-001--emit-useful-bounded-and-safe-diagnostic-logs) | Required* | Review/tests | Safe bounded diagnostics |
| [RCS-TEST-001](rules/testing.md#rcs-test-001--make-tests-deterministic-and-owned) | Required | Tests/review | Synthetic fixture isolation |
| [RCS-TEST-002](rules/testing.md#rcs-test-002--verify-real-failure-modes) | Required* | Tests/review | Negative-path coverage |
| [RCS-TEST-003](rules/testing.md#rcs-test-003--organize-tests-around-behavioral-contracts-and-named-cases) | Advisory | Review | Behavioral tests with named cases |
| [RCS-DOC-001](rules/testing.md#rcs-doc-001--document-nonobvious-contracts) | Advisory | Rustdoc/review | Important invariants |
| [RCS-TOOL-001](rules/concurrency-and-tooling.md#rcs-tool-001--align-formatting-edition-and-lint-expectations) | Advisory | rustfmt/Clippy/review | Align edition, format and lints |
| [RCS-TOOL-002](rules/concurrency-and-tooling.md#rcs-tool-002--test-the-supported-contract-not-a-convenient-subset) | Required* | CI/review | Validate actual supported targets |

**Required*** means required when that rule's stated applicability condition holds (for example, user-owned data or a large-file hot path), not when an unrelated project feature is absent.

## Using these rules in a code review

Follow the [reviewer guide](review-guide.md) to select applicable rule IDs, trace affected call paths, record evidence-backed findings, and separate correctness defects from optional suggestions. A consuming repository must explicitly adopt these rules (normally the latest `main`, or an intentional fixed revision) before they are binding requirements.

## Application

Review standards in proportion to the change. A library API and a private command-line module have different concerns; a one-time small string operation and repeated multi-gigabyte image hashing have different costs.

**Do not weaken** existing identity checks, concurrency guarantees, input validation, recovery proof or data-integrity constraints just to satisfy a performance or simplicity suggestion. Safety-critical patterns are useful as references but no external certification or unpublished preview is incorporated wholesale.

## Evidence and exceptions

When a rule warrants an actionable finding, record **ID → path/symbol → concrete trigger → consequence → smallest safe fix/test**. Label stylistic suggestions separately.

An adopting project may explain an exception inline near the code or in its own rules/ADR. A documented exception must still satisfy the project's actual functional and safety contracts. A large but cohesive module can be entirely acceptable; numerical file-size or method-count limits are not part of these standards.

See [Sources and attribution](sources.md) for upstream materials and attribution.
