# Style and structure

These conventions are based on ordinary Rust tooling and the design goals of a shared coding standard. The rules below are original guidance, not copied from upstream.

## ZR-FMT-001 — Format with rustfmt {#zr-fmt-001--format-with-rustfmt}

**Level:** Required for Rust source in the adopter's declared scope.

**Enforcement:** `cargo fmt --all -- --check`; CI or local review.

Use the project's reviewed `rustfmt` configuration (or the tool's defaults) consistently. Avoid manually aligning columns, fighting the formatter, or changing formatting settings casually to justify unrelated changes.

```sh
cargo fmt --all -- --check
```

A formatting diff alone is not evidence of a correctness defect. Do not create an unbounded unrelated reformatting PR in the middle of a behavioral fix.

## ZR-NAME-001 — Use idiomatic names {#zr-name-001--use-idiomatic-names}

**Level:** Required when naming new Rust code; backward-compatible public APIs may retain established names.

**Enforcement:** `rustc`/Clippy naming lints and reviewer understanding.

Use `snake_case` for modules, functions and variables; `UpperCamelCase` for types and traits; `SCREAMING_SNAKE_CASE` for constants. Names should identify *what* a value represents, not merely its storage type.

Preferred:

```rust
struct CollectionId(String);

const MAX_DISCOVERED_ENTRIES: usize = 4_096;

fn collection_id_is_present(id: &CollectionId) -> bool {
    !id.0.is_empty()
}
```

Avoid abbreviations only the original author understands, misleading security/authority names (`verified`, `trusted`, `atomic` without proof), and names that encode a different purpose from the value's actual contents.

A local product may require different established public naming conventions; write down a scoped exception instead of silently renaming its API.

## ZR-MOD-001 — Organize by responsibility {#zr-mod-001--organize-by-responsibility}

**Level:** Advisory.

**Enforcement:** Human review, call-path analysis and tests.

Keep a module's public contract cohesive. Consider extracting a separate module when several unrelated responsibilities must evolve independently, when readers cannot find invariants, or when tests exercise unrelated concerns through the same large entry point.

Prefer a narrow structure such as:

```text
filesystem/
  identity.rs     # platform object identity
  copy_plan.rs    # reviewed operation description
  verify.rs       # output integrity checks
  mod.rs          # intentionally small public boundary
```

This is only an illustrative design, not a mandated module layout. A larger cohesive module may be clearer than several tiny layers. **Do not impose an arbitrary line count**, introduce interfaces for a single known implementation without benefit, or split a change merely to meet a PR-size metric.

**Review question:** Would an experienced Rust maintainer understand the behavior, responsibilities, and failure paths without reconstructing a maze of wrappers?

[Back to standards index](../standards.md).
