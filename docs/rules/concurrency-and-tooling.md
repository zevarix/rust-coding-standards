# Concurrency and toolchain discipline

Concurrency correctness and mechanical tooling require evidence about actual behavior. These rules do not mandate asynchronous Rust, a particular runtime, or every optional Clippy lint.

## RCS-CONC-001 — Make shared-state invariants atomic at the right boundary {#rcs-conc-001--make-shared-state-invariants-atomic-at-the-right-boundary}

**Level:** Required when multiple threads/tasks can update the same consequential counter, reservation, generation, work queue or durable state.

**Enforcement:** Trace read/modify/write and lock scope across all writers; synthetic contention, stale-generation, cancellation and recovery tests.

### Requirement

A read followed by a separate write is not an atomic reservation. Protect the **complete invariant** with an appropriate transaction, lock, CAS or other synchronization boundary. Match atomic ordering to actual cross-thread communication; an atomic count cannot replace a database transaction or prove a physical file effect.

**Avoid** a split load/check/store under contention:

```rust
let prior = admitted.load(std::sync::atomic::Ordering::Relaxed);
if prior < cap {
    admitted.store(prior + 1, std::sync::atomic::Ordering::Relaxed);
    // Two workers can both observe the same prior value.
}
```

**Prefer** a single atomic admission decision for a purely in-memory quota:

<!-- rcs-example: test -->
```rust
use std::sync::{Arc, atomic::{AtomicU64, Ordering}};

pub fn reserve_one(counter: &AtomicU64, cap: u64) -> bool {
    counter.try_update(Ordering::AcqRel, Ordering::Acquire, |old| {
        old.checked_add(1).filter(|next| *next <= cap)
    }).is_ok()
}

#[test]
fn contention_does_not_over_admit() {
    let counter = Arc::new(AtomicU64::new(0));
    let workers: Vec<_> = (0..8).map(|_| {
        let counter = Arc::clone(&counter);
        std::thread::spawn(move || reserve_one(&counter, 3))
    }).collect();

    let admitted = workers.into_iter()
        .map(|handle| handle.join().expect("synthetic worker panicked"))
        .filter(|granted| *granted)
        .count();
    assert_eq!(admitted, 3);
    assert_eq!(counter.load(Ordering::Acquire), 3);
}
```

This proves one in-process quota invariant for the test's execution, **not** general crash recovery, cross-process admission, lock-free algorithm correctness or freedom from every possible concurrency race. Durable reservations need the owning store's transactional guarantees and reconciliation.

### Reviewer check

List all writers and their exact shared objects, not only the function under review. Find stale snapshots, read/modify/write sequences, inconsistent lock order, lock-held blocking I/O, cloned handles with hidden authority, and cancellation paths that bypass state release. Test competing attempts, stale generations and interrupted reservations with deterministic barriers where they improve the evidence.

**Exception:** Data that is exclusively owned by one task/thread, immutable inputs, and independent work items do not need global locks or atomic bookkeeping. Do not introduce concurrency just for throughput speculation.

**Source:** [Rust atomic operations](https://doc.rust-lang.org/std/sync/atomic/).

## RCS-TOOL-001 — Align formatting, edition and lint expectations {#rcs-tool-001--align-formatting-edition-and-lint-expectations}

**Level:** Advisory, except that a project's declared required formatter/linter settings must be applied consistently when checking its code.

**Enforcement:** Confirm the actual `Cargo.toml` Rust edition, toolchain, `rustfmt` style edition/editor behavior, and the locally configured Clippy commands.

### Requirement

Prefer `cargo fmt --all -- --check` against the project's actual toolchain and formatting contract. Rust's **language edition** and `rustfmt` **style edition** are related but distinct; direct editor `rustfmt` invocations can choose different defaults from `cargo fmt`. For projects using Rust 2024 formatting intentionally, a `rustfmt.toml` can declare:

```toml
style_edition = "2024"
```

When the application declares edition 2024 in `Cargo.toml`, `cargo fmt` ordinarily derives the corresponding style edition; a project-wide configuration helps direct formatter/editor invocations stay aligned. Introduce a style-edition migration deliberately instead of burying mass reformatting inside a behavior fix.

Run Clippy with the **target/features that actually compile in this project**, selecting a stable baseline such as:

```sh
cargo clippy --all-targets
```

If the project expressly treats chosen Clippy warnings as errors, then its own check may add `-- -D warnings`. Do **not** automatically require `clippy::pedantic`, `clippy::nursery`, `--all-features`, `-D warnings` or a particular paid reviewer across every consumer. A lint is evidence to investigate, not proof that more wrappers or larger code rewrites are safer.

### Reviewer check

Identify the claimed toolchain and flags, inspect actual diagnostics and note skipped targets/features; distinguish a formatting difference from a correctness finding. If an automated check is not installed or a target cannot compile locally, state the gap without claiming it passed. Avoid using a new compiler's suggestions to silently change an accepted compatibility baseline.

**Source:** [Rust 2024 rustfmt style edition](https://doc.rust-lang.org/edition-guide/rust-2024/rustfmt-style-edition.html), [Clippy guidance](https://doc.rust-lang.org/clippy/usage.html).

## RCS-TOOL-002 — Test the supported contract, not a convenient subset {#rcs-tool-002--test-the-supported-contract-not-a-convenient-subset}

**Level:** Required when a change's acceptance depends on platform-specific behavior, selected Cargo features, parser behavior or recovery semantics.

**Enforcement:** Project-owned test matrix, actual toolchain/version readback, target-appropriate synthetic fixtures and truthful results per platform.

### Requirement

Choose validation from the *consumer's declared supported targets and behavior*, not from a universal list of commands. For applications, a committed `Cargo.lock` and `--locked` checks can improve repeatability; libraries may choose a different lockfile policy. Distinguish `cargo check` (type checking) from `cargo test` (executing tests), Clippy warnings from tests, and source compilation from native filesystem acceptance.

For example, a project might run:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
cargo test --locked
```

These commands are **illustrative**, not mandatory universal flags: the adopting project decides whether `-D warnings`, `--locked`, feature matrices and platform testing are required. Running tests on Windows alone cannot prove macOS or Linux pathname, handle or atomic-publication behavior. When a platform is unavailable, preserve the acceptance gap instead of fabricating a PASS.

### Reviewer check

For each consequential change, trace its intended platform/features and failure conditions to executed test evidence. Verify whether a test actually exercised the release-built path or only a synthetic/test-gated variant. Check negative scenarios, dirty-input races, and failure-injection placement; use the smallest supported matrix that proves the affected behavior without forcing unrelated systems to rebuild unnecessarily.

**Exception:** A purely portable local documentation or internal refactor may need much narrower validation than a filesystem adapter or toolchain upgrade. Extra CI checks should earn their cost and not become arbitrary approval hurdles.

**Sources:** [Cargo testing](https://doc.rust-lang.org/cargo/commands/cargo-test.html), [Cargo lockfile](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html), [Clippy](https://doc.rust-lang.org/clippy/).

[Back to standards index](../standards.md).
