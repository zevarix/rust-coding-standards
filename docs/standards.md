# Rust Coding Standards — Draft 0.1

These are **proposed shared rules**, not accepted policy for every Zevarix repository. An adopter controls the pinned revision, scope, explicit exceptions, and any stronger local rules. Code that predates adoption is not automatically noncompliant.

## Rule levels

- **Required:** the default expectation *within an adopting project's declared scope*. Deviations need a locally documented technical reason, not permission from this repository.
- **Advisory:** a preferred design or review question. Departures may be sensible and are not automatic review failures.

For either level, reviewers report demonstrated problems with a concrete call path, trigger and impact. A rule name by itself is not proof of a defect. Tool errors block only the affected validation claim or operation; they do not end unrelated safe progress.

## Index

| Rule | Level | Enforced by | Concern |
| --- | --- | --- | --- |
| [ZR-FMT-001](rules/style-and-structure.md#zr-fmt-001--format-with-rustfmt) | Required | `rustfmt` | Consistent Rust formatting |
| [ZR-NAME-001](rules/style-and-structure.md#zr-name-001--use-idiomatic-names) | Required | Compiler/Clippy + review | Naming conventions |
| [ZR-MOD-001](rules/style-and-structure.md#zr-mod-001--organize-by-responsibility) | Advisory | Human review | Cohesive modules, not line quotas |
| [ZR-TYPE-001](rules/types-and-errors.md#zr-type-001--model-consequential-identities-distinctly) | Required* | Review/tests | Prevent identity/unit mixups |
| [ZR-API-001](rules/types-and-errors.md#zr-api-001--follow-predictable-api-conventions) | Advisory | Review/Clippy | Conventional Rust APIs |
| [ZR-ERR-001](rules/types-and-errors.md#zr-err-001--use-explicit-recoverable-errors) | Required | Review/Clippy/tests | `Result` and error propagation |
| [ZR-ERR-002](rules/types-and-errors.md#zr-err-002--preserve-actionable-boundary-context) | Advisory | Human review/tests | Diagnostic boundaries |
| [ZR-SAFE-001](rules/safety.md#zr-safe-001--justify-unsafe-operations) | Required* | Review/tests | `unsafe` soundness |
| [ZR-DATA-001](rules/safety.md#zr-data-001--protect-user-owned-data) | Required* | Review/tests | Non-destructive defaults |
| [ZR-PERF-001](rules/performance.md#zr-perf-001--review-work-across-call-paths) | Required* | Review/instrumentation | Avoid costly duplicate work |
| [ZR-PERF-002](rules/performance.md#zr-perf-002--optimize-with-evidence) | Advisory | Profiling/review | Avoid premature optimization |
| [ZR-TEST-001](rules/testing.md#zr-test-001--make-tests-deterministic-and-owned) | Required | Tests/review | Synthetic fixture isolation |
| [ZR-TEST-002](rules/testing.md#zr-test-002--verify-real-failure-modes) | Required* | Tests/review | Negative-path coverage |
| [ZR-DOC-001](rules/testing.md#zr-doc-001--document-nonobvious-contracts) | Advisory | Rustdoc/review | Important invariants |

**Required*** means required when that rule's stated applicability condition holds (for example, user-owned data or a large-file hot path), not when an unrelated project feature is absent.

## Application

Review standards in proportion to the change. A library API and a private command-line module have different concerns; a one-time small string operation and repeated multi-gigabyte image hashing have different costs.

**Do not weaken** existing identity checks, concurrency guarantees, input validation, recovery proof or data-integrity constraints just to satisfy a performance or simplicity suggestion. Safety-critical patterns are useful as references but no external certification or unpublished preview is incorporated wholesale.

## Evidence and exceptions

When a rule warrants an actionable finding, record **ID → path/symbol → concrete trigger → consequence → smallest safe fix/test**. Label stylistic suggestions separately.

An adopting project may explain an exception inline near the code or in its own rules/ADR. A documented exception must still satisfy the project's actual functional and safety contracts. A large but cohesive module can be entirely acceptable; numerical file-size or method-count limits are not part of these standards.

See [SOURCES.md](sources.md) for upstream materials and attribution.
