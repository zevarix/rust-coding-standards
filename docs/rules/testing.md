# Testing and documentation

## RCS-TEST-001 — Make tests deterministic and owned {#rcs-test-001--make-tests-deterministic-and-owned}

**Level:** Required for automated tests in the adopter's scope.

**Enforcement:** Test suite, fixture inspection and review.

Tests must own the objects they create and modify. Filesystem tests should operate inside disposable test-created directories, not user home directories, real collections or arbitrary external paths. Synthetic, redistributable bytes should suffice for normal regression testing.

Example using the optional `tempfile` development dependency:

```rust
#[test]
fn writes_only_to_owned_test_tree() -> std::io::Result<()> {
    let temp = tempfile::tempdir()?;
    let path = temp.path().join("invented.bin");

    std::fs::write(&path, b"synthetic test bytes")?;
    assert_eq!(std::fs::read(&path)?, b"synthetic test bytes");
    Ok(())
}
```

A test capable of deleting or overwriting user files should include a stronger guard than "we hope the path is temporary": verify a test-owned root and refuse operations outside it before mutation. The exact fence is project-specific.

## RCS-TEST-002 — Verify real failure modes {#rcs-test-002--verify-real-failure-modes}

**Level:** Required where code guards identity, data integrity, recovery, untrusted input or other consequential behavior.

**Enforcement:** Focused negative tests plus review of what they actually prove.

In addition to the happy path, test the behavior when one key assumption is false:

- The source or expected digest changes after a reviewed observation.
- A destination collides or a parent is redirected.
- A write is interrupted before durable completion.
- A provider returns malformed, partial or stale data.
- A SQLite transaction fails at a boundary that must preserve previous state.

A green test count is not proof of atomicity, cross-platform behavior, realistic I/O performance or recovery. Test the right failure cause and verify the sentinel/unchanged state where material.

Do not require every project to implement irrelevant platform-specific tests or artificial fault-injection machinery.

## RCS-DOC-001 — Document nonobvious contracts {#rcs-doc-001--document-nonobvious-contracts}

**Level:** Advisory for internal helpers; stronger documentation may be required for public APIs and unsafe contracts.

**Enforcement:** Rustdoc plus human review.

Explain the *why* where code alone cannot: safety boundaries, irreversible actions, namespace assumptions, external effects, invariants and what a returned observation **does not** authorize.

```rust
/// Observe the candidate output path without creating it.
///
/// The report describes a momentary filesystem state, not permission
/// to overwrite, promote, publish or reclaim a source file.
fn inspect_destination_read_only(/* parameters omitted */) {
    // ...
}
```

Avoid comments that merely narrate a statement, stale descriptions of past code, or claims of stronger guarantees than the implementation actually proves. Prefer stable, current descriptions and explicit fallibility.

[Back to standards index](../standards.md).
