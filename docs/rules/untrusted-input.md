# Untrusted inputs and bounded work

Parsing files, archives, network responses or external-tool output is not automatically safe merely because it is written in safe Rust. These rules apply when untrusted size, count, nesting or field values drive resource use or correctness.

## RCS-INPUT-001 — Bound actual work, not just declared sizes {#rcs-input-001--bound-actual-work-not-just-declared-sizes}

**Level:** Required when malformed or adversarial content can drive significant memory, disk, CPU, nesting, member count or decompression work.

**Enforcement:** Review where input values become allocations or loops; test limits and negative paths with synthetic bytes, including a stream that produces more output than its metadata advertises.

### Requirement

Define a meaningful per-operation budget and enforce it **as work occurs**, including across nested operations. Validate declared metadata early but do not treat it as evidence of actual decompressed size. Reject overflow, excessive output, recursion/member explosion or time/resource exhaustion without constructing a partially trusted success result.

**Avoid** assuming a header controls real expansion:

```rust
let declared = entry.declared_uncompressed_size();
let bytes = decompress_to_end(entry)?; // Actual output may exceed declared size.
assert!(bytes.len() <= declared as usize);
```

**Prefer** checking each output chunk against a cumulative budget (this example accounts for bytes only; real archive readers additionally bound depth, members, allocation and elapsed work when relevant):

<!-- rcs-example: test -->
```rust
#[derive(Debug, PartialEq, Eq)]
pub enum BudgetError {
    UnrepresentableChunk,
    Overflow,
    Exceeded,
}

pub fn account_output(used: u64, chunk_bytes: usize, cap: u64) -> Result<u64, BudgetError> {
    let chunk = u64::try_from(chunk_bytes).map_err(|_| BudgetError::UnrepresentableChunk)?;
    let next = used.checked_add(chunk).ok_or(BudgetError::Overflow)?;
    if next > cap {
        return Err(BudgetError::Exceeded);
    }
    Ok(next)
}

#[test]
fn rejects_output_beyond_cap() {
    assert_eq!(account_output(6, 4, 10), Ok(10));
    assert_eq!(account_output(6, 5, 10), Err(BudgetError::Exceeded));
    assert_eq!(account_output(u64::MAX, 1, u64::MAX), Err(BudgetError::Overflow));
}
```

The caller must **not write, allocate or trust a chunk before checking it** when the budget protects that side effect. In a streaming decompressor, a bounded destination/sink should enforce limits during production, not merely reject after full expansion. Intentional format-specific limits belong to the owning product, not universal numbers in this guide.

### Reviewer check

Trace input metadata → repeated decode/iteration → actual consumed bytes/entries/depth → allocation or output effect. Check whether one nested operation can reset a shared budget, whether integer conversions truncate, and whether a rejected operation preserves previous state. Test malformed headers, oversized output, nested bombs and multiple entries that individually fit but collectively exceed the cap.

**Exception:** Truly bounded trusted in-memory values may not need additional resource accounting. A small local parser can use a simpler limit than a nested multi-gigabyte archive processor.

**Sources:** [`Read` trait](https://doc.rust-lang.org/std/io/trait.Read.html), [checked arithmetic](https://doc.rust-lang.org/std/primitive.u64.html#method.checked_add).

## RCS-INPUT-002 — Make malformed or partial input outcomes explicit {#rcs-input-002--make-malformed-or-partial-input-outcomes-explicit}

**Level:** Required when parsed values affect identity, persisted state, authorization, output location or other consequential decisions.

**Enforcement:** Negative tests for truncation, trailing data, invalid encoding, unsupported versions, duplicates and missing required fields; review return types and caller behavior.

### Requirement

Parse the actual supplied bytes using fallible APIs and distinguish **complete verified input**, **explicitly partial usable data** and **invalid/unsupported content** where the application needs those states. Never silently fill missing identity fields, return a default valid digest, or interpret malformed provider output as trustworthy success.

**Avoid** untrusted indexing and implied format acceptance:

```rust
let size = u32::from_le_bytes(bytes[0..4].try_into().unwrap());
```

**Prefer** a fallible contract with exact field-width checking:

<!-- rcs-example: test -->
```rust
#[derive(Debug, PartialEq, Eq)]
pub enum HeaderError {
    WrongLength,
}

pub fn decode_size_field(bytes: &[u8]) -> Result<u32, HeaderError> {
    let field: &[u8; 4] = bytes.try_into().map_err(|_| HeaderError::WrongLength)?;
    Ok(u32::from_le_bytes(*field))
}

#[test]
fn rejects_truncation_and_trailing_bytes() {
    assert_eq!(decode_size_field(&[9, 0, 0, 0]), Ok(9));
    assert_eq!(decode_size_field(&[9, 0, 0]), Err(HeaderError::WrongLength));
    assert_eq!(decode_size_field(&[9, 0, 0, 0, 0]), Err(HeaderError::WrongLength));
}
```

This narrow example validates one fixed-width field. Full parsers must also validate frame boundaries, meaningful invariants and legal trailing sections for the *actual format*. Streaming or best-effort APIs may return useful partial results if the return type exposes their uncertainty and downstream consumers handle it deliberately.

### Reviewer check

Identify the first place data becomes authoritative. Ask which malformed inputs can reach it, whether parser errors are propagated or converted to permissive defaults, and whether data is committed before full validation. Test rejected input leaves prior persisted or external state unchanged.

**Exception:** Presentation-only best-effort fields can reasonably use defaults when they do not control identity, authority or consequential output.

**Sources:** [`TryFrom`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html), [`Read::read_exact`](https://doc.rust-lang.org/std/io/trait.Read.html#method.read_exact).

[Back to standards index](../standards.md).
