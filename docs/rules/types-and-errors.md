# Types, APIs and errors

## ZR-TYPE-001 — Model consequential identities distinctly {#zr-type-001--model-consequential-identities-distinctly}

**Level:** Required when accidentally interchanging same-primitive values would materially affect correctness or safety.

**Enforcement:** Compiler type checking, focused tests and human review.

Do not pass logically distinct identities interchangeably as loose strings or integers when their confusion could change the operation's target.

Avoid:

```rust
fn bind(source_id: &str, target_id: &str) {
    // Both arguments are strings: swapping them still type-checks.
}

bind("target-17", "source-42");
```

Prefer:

```rust
#[derive(Clone, Debug, Eq, PartialEq)]
struct SourceId(String);

#[derive(Clone, Debug, Eq, PartialEq)]
struct TargetId(String);

fn bind(source_id: &SourceId, target_id: &TargetId) {
    // The compiler distinguishes source and target identities.
}
```

The example is intentionally small. Real constructors should validate externally supplied IDs. A newtype is **not** mandatory for every internal counter, temporary string or obvious local value: use it where the type carries a meaningful invariant.

## ZR-API-001 — Follow predictable API conventions {#zr-api-001--follow-predictable-api-conventions}

**Level:** Advisory for public or broadly reused Rust APIs.

**Enforcement:** Review, Rustdoc and relevant Clippy lints.

- Choose clear constructors (often `new`) and use conventional trait implementations when they make behavior unambiguous.
- Prefer borrowing when ownership transfer is not needed; avoid repeated allocations merely to satisfy a convenient signature.
- Expose the narrowest useful public surface rather than exporting internal state or implementation details.
- Use intuitive getters and method names. If an operation is fallible, expose that fact in its return type.
- Document non-obvious invariants and resource lifetimes where users need them.

Avoid introducing wrapper types and traits for hypothetical future integrations without a concrete consumer. Consult the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html), but apply public-library advice proportionally to private application code.

## ZR-ERR-001 — Use explicit recoverable errors {#zr-err-001--use-explicit-recoverable-errors}

**Level:** Required on a path that can fail because of I/O, malformed input, provider output, or other expected environmental conditions.

**Enforcement:** Code review, Clippy and negative-path tests.

Prefer `Result` with ordinary `?` propagation instead of hiding errors, unconditionally panicking on untrusted inputs or returning guessed success values.

Preferred:

```rust
use std::{fs::File, io::{self, Read}, path::Path};

fn read_magic(path: &Path) -> io::Result<[u8; 4]> {
    let mut file = File::open(path)?;
    let mut magic = [0_u8; 4];
    file.read_exact(&mut magic)?;
    Ok(magic)
}
```

A failed I/O read must not produce an invented digest or a partially trusted state. `expect`/`unwrap` remain reasonable in tests, examples and contexts with proven invariants; a blanket ban is not intended.

## ZR-ERR-002 — Preserve actionable boundary context {#zr-err-002--preserve-actionable-boundary-context}

**Level:** Advisory.

**Enforcement:** Human review and error-path testing.

Errors should identify the failed *operation class* or contract at the point where callers can act on it. Avoid error enums that collapse all failures into an unhelpful boolean or indiscriminately convert dangerous ambiguity into "not found."

Prefer typed errors and meaningful context where it improves recovery. Do not build a deep error-wrapper hierarchy if simple standard errors remain expressive.

[Back to standards index](../standards.md).
