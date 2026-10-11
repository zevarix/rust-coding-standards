# Numbers, sizes and bounds

Rust makes arithmetic behavior explicit when you choose the appropriate operations. The relevant question in review is whether a value can exceed its valid range and what the caller does when that happens. Ordinary local arithmetic does not need a new wrapper for every expression.

## RCS-NUM-001 — Check consequential arithmetic {#rcs-num-001--check-consequential-arithmetic}

**Level:** Required when overflow or underflow could change a file offset, allocation size, length, capacity, monetary quantity, protocol field, or other consequential decision.

**Enforcement:** Reviewer traces operands from their sources; boundary tests; Rust's checked arithmetic where appropriate. Clippy helps with some patterns, but does not establish the intended overflow policy.

### Requirement

Do not rely on differences between debug and optimized builds to decide what happens when a critical calculation exceeds its range. Use checked arithmetic and return a meaningful error or absence when an invalid result must be rejected. Use saturating or wrapping arithmetic **only** when that behavior is part of the documented algorithm.

**Avoid** when the operands are external file sizes:

```rust
// A too-large total is not a valid file range.
let end = start + length;
```

**Prefer** when an overflowing range is invalid:

<!-- rcs-example: test -->
```rust
#[derive(Debug, PartialEq, Eq)]
pub enum RangeError {
    Overflow,
}

pub fn end_offset(start: u64, length: u64) -> Result<u64, RangeError> {
    start.checked_add(length).ok_or(RangeError::Overflow)
}

#[test]
fn rejects_overflowing_offset() {
    assert_eq!(end_offset(u64::MAX, 1), Err(RangeError::Overflow));
    assert_eq!(end_offset(12, 3), Ok(15));
}
```

This example checks the arithmetic only. A real reader must also prove that the resulting range is inside the actual file and that the file identity is current.

### Reviewer check

- Follow both operands to their source; decide whether attacker-controlled, machine-dependent, or ordinary trusted in-memory values can reach the expression.
- Check additions, subtractions, multiplications, and derived ranges that feed consequential decisions; verify the caller handles the failure branch instead of substituting zero or silently skipping it.
- Test at and just beyond meaningful boundaries, not by counting arbitrary occurrences of `+`.
- Wrapping checksums, bitwise algorithms, and clearly bounded local loop counters may intentionally use different behavior; document that reason when it is not obvious.

**Source:** [Rust checked integer arithmetic](https://doc.rust-lang.org/std/primitive.u64.html#method.checked_add).

## RCS-NUM-002 — Reject lossy conversions where identity or size matters {#rcs-num-002--reject-lossy-conversions-where-identity-or-size-matters}

**Level:** Required when changing an integer width or sign could alter an offset, size, index, identifier, serialized field, or other consequential value.

**Enforcement:** Reviewer checks casts at input/output boundaries, uses `TryFrom`/`TryInto` when a value might not fit, and tests edge values.

### Requirement

A bare integer `as` cast can silently discard high bits or reinterpret values. When an out-of-range value is invalid, use a fallible conversion and make the failure visible. A checked conversion is **not** a substitute for application limits: a value can fit the type and still be too large to allocate or write safely.

**Avoid** when exporting a size into a 32-bit field:

```rust
let encoded_length = file_size as u32;
```

**Prefer**:

<!-- rcs-example: test -->
```rust
#[derive(Debug, PartialEq, Eq)]
pub enum EncodeError {
    TooLarge,
}

pub fn encode_length(file_size: u64) -> Result<u32, EncodeError> {
    u32::try_from(file_size).map_err(|_| EncodeError::TooLarge)
}

#[test]
fn rejects_unrepresentable_length() {
    assert_eq!(encode_length(42), Ok(42));
    assert_eq!(
        encode_length(u64::from(u32::MAX) + 1),
        Err(EncodeError::TooLarge)
    );
}
```

### Reviewer check

Identify the narrower destination type and the largest possible source value. Check the error returned for negative or excessive inputs, plus target-platform widths such as `usize`. Look for truncation in file formats, database columns, offsets, FFI parameters, and array indexing.

**Reasonable exceptions:** deliberate mask/truncation in a documented binary protocol, cryptographic or modular arithmetic, and casts whose representable range is already proven by an invariant. Do not ban all `as` casts.

**Sources:** [Fallible conversions](https://doc.rust-lang.org/std/convert/trait.TryFrom.html), [Rust standard conversion traits](https://doc.rust-lang.org/std/convert/).
