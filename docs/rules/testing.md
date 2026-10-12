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

## RCS-TEST-003 — Organize tests around behavioral contracts and named cases {#rcs-test-003--organize-tests-around-behavioral-contracts-and-named-cases}

**Level:** Advisory. It becomes especially useful when several tests repeat the same
setup/operation/outcome shape for different input states.

**Enforcement:** Human review of test intent, failure output and duplicated setup; refactor
only when grouping preserves or improves diagnosis.

### Requirement

Treat one test function as one **independently meaningful behavioral contract**, not as one
branch, assertion or input combination.

When several scenarios exercise the same contract with the same essential setup,
operation and outcome shape, prefer a compact table/array of **named cases** over one
`#[test]` per scenario. Each case should carry enough human-readable identity that a
failure names the scenario that broke.

Do not optimize for the smallest possible test-function count. Keep separate tests when
scenarios have materially different setup, external effects, recovery semantics, platform
requirements, failure contracts, or when grouping would make a failure harder to
understand.

Prefer a small named case struct once positional tuples become difficult to scan. The
field names should make the behavior matrix readable without forcing a future maintainer
to mentally decode several booleans or IDs.

Do not force table-driven structure when only one meaningful scenario exists or when
parameterization adds more indirection than clarity. Shared helpers/case setup must not
hide the important precondition the test is supposed to prove.

The purpose is **human-readable executable documentation and maintainable coverage**:
adding another equivalent scenario should usually mean adding a case, while adding a new
behavioral contract should usually mean adding a test.

### Example: one selection contract with named cases

<!-- rcs-example: test -->
```rust
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Presentation {
    Interactive,
    Plain,
}

fn presentation(is_terminal: bool, plain_requested: bool) -> Presentation {
    if is_terminal && !plain_requested {
        Presentation::Interactive
    } else {
        Presentation::Plain
    }
}

struct Case {
    name: &'static str,
    is_terminal: bool,
    plain_requested: bool,
    expected: Presentation,
}

#[test]
fn presentation_respects_terminal_and_plain_mode() {
    let cases = [
        Case {
            name: "redirected",
            is_terminal: false,
            plain_requested: false,
            expected: Presentation::Plain,
        },
        Case {
            name: "plain requested",
            is_terminal: true,
            plain_requested: true,
            expected: Presentation::Plain,
        },
        Case {
            name: "interactive terminal",
            is_terminal: true,
            plain_requested: false,
            expected: Presentation::Interactive,
        },
    ];

    for case in cases {
        assert_eq!(
            presentation(case.is_terminal, case.plain_requested),
            case.expected,
            "case: {}",
            case.name,
        );
    }
}
```

The three rows are examples of the same presentation-selection contract. A scenario that
needed different terminal cleanup, subprocess effects or recovery assertions would likely
deserve a separate test rather than another row.

### Reviewer check

- Read the test name: does it describe one behavior/contract rather than an implementation
  branch or incidental input?
- Look for clusters of nearly identical tests. If only the input/expected value changes,
  would named cases make the behavior matrix easier to scan and extend?
- Check that each grouped case identifies itself in failure output.
- Prefer a named struct when tuple positions or boolean combinations are hard to decipher.
- Do not combine tests whose setup, effects, recovery guarantees or platform contracts are
  independently meaningful.
- Do not treat fewer test functions as a quality metric. The refactor should reduce
  duplication or improve comprehension without weakening coverage.
- Verify shared helpers do not conceal the exact failure precondition.

**Exceptions:** Property tests, fuzz targets, compile-fail suites, macro-generated tests,
platform harnesses and framework-native parameterized tests may already provide their own
case identity and execution model. Use the underlying principle rather than wrapping them
in another table solely for stylistic uniformity.

**Related:** [RCS-TEST-001](#rcs-test-001--make-tests-deterministic-and-owned) and
[RCS-TEST-002](#rcs-test-002--verify-real-failure-modes).

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
