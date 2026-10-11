# Safety and user-owned data

These rules apply when a Rust project handles native FFI, untrusted input, or consequential user data. A small pure arithmetic library need not invent a filesystem approval protocol.

## ZR-SAFE-001 — Justify unsafe operations {#zr-safe-001--justify-unsafe-operations}

**Level:** Required wherever `unsafe` is necessary.

**Enforcement:** Human review of the exact unsafe operation, tests and optional focused analysis tools.

Prefer safe Rust when it expresses the same contract. When an unsafe FFI or pointer operation is unavoidable, keep its scope narrow and document the *actual proof obligations* (validity, ownership, alignment, initialization, lifetime, aliasing, concurrency and error behavior) relevant to it.

Illustrative narrow function:

```rust
/// Read one initialized byte through a raw pointer.
///
/// # Safety
/// The caller must provide a non-null pointer valid to read one initialized
/// byte, with no concurrent mutation conflicting with this read.
pub unsafe fn read_byte(ptr: *const u8) -> u8 {
    // SAFETY: the documented caller contract guarantees that the pointer
    // refers to a readable, initialized byte for this access.
    unsafe { ptr.read() }
}
```

A comment by itself never proves soundness: review how the preconditions are established and preserved by callers. Prefer a safe wrapper around a narrowly audited unsafe primitive when possible.

Do not claim all FFI is automatically unsafe in the same way. On Windows, Unix and macOS, the applicable handle, sharing, error and path semantics require platform-specific evidence.

## ZR-DATA-001 — Protect user-owned data {#zr-data-001--protect-user-owned-data}

**Level:** Required when operating on user-owned files, archives, databases or other consequential external state.

**Enforcement:** Tests, explicit authority boundaries and human review.

Read-only discovery should not silently become a mutation. For writes, make the intended destination and side effects inspectable, respect the project's authority model, refuse ambiguous targets, and preserve recovery or rollback evidence when the operation warrants it.

Avoid overwriting an existing file through an unchecked convenience operation:

```rust
// Example of an unsafe default for consequential output paths:
std::fs::write(path, bytes)?;
```

A safer *starting point* for exclusive new-file creation is:

```rust
use std::{fs::{File, OpenOptions}, io, path::Path};

fn create_absent_file(path: &Path) -> io::Result<File> {
    OpenOptions::new().write(true).create_new(true).open(path)
}
```

**Important:** `create_new` does **not** by itself prove safe ancestry, namespace isolation, reserved space, atomic durable promotion or authorization. Never treat this example as a complete secure copy/extraction implementation.

Preserve source originals unless an independently authorized, separately verified reclaim operation permits otherwise. A valid plan, proven destination identity, bounded decompression, content-integrity recheck and interruption recovery belong to the owning product's contract, not to an invented universal Rust policy.

[Back to standards index](../standards.md).
