# Style and structure

These conventions are based on ordinary Rust tooling and the design goals of a shared coding standard. The rules below are original guidance, not copied from upstream.

## RCS-FMT-001 — Format with rustfmt {#rcs-fmt-001--format-with-rustfmt}

**Level:** Required for Rust source in the adopter's declared scope.

**Enforcement:** `cargo fmt --all -- --check`; CI or local review.

Use the project's reviewed `rustfmt` configuration (or the tool's defaults) consistently. Avoid manually aligning columns, fighting the formatter, or changing formatting settings casually to justify unrelated changes.

```sh
cargo fmt --all -- --check
```

A formatting diff alone is not evidence of a correctness defect. Do not create an unbounded unrelated reformatting PR in the middle of a behavioral fix.

## RCS-NAME-001 — Use idiomatic names {#rcs-name-001--use-idiomatic-names}

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

## RCS-MOD-001 — Organize by responsibility {#rcs-mod-001--organize-by-responsibility}

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

## RCS-META-001 — Derive package release versions from their authority {#rcs-meta-001--derive-package-release-versions-from-their-authority}

**Level:** Advisory for executable/library code that displays or embeds its own
*package release version*.

**Enforcement:** Review package/build metadata and user-visible version output;
where practical, test that the release string follows the actual package
version without a second source edit.

### Guidance

Use the existing package/build definition as the source of truth for its
release version. Avoid repeating a literal such as `v0.1.0` in CLI help text,
log banners or application labels when that text is meant to represent the
currently built package. In a Cargo package, built-in compile-time metadata
avoids a separately maintained version string, build script or dependency:

```rust
pub const RELEASE_VERSION: &str = env!("CARGO_PKG_VERSION");

pub fn product_banner() -> String {
    format!("ExampleApp {RELEASE_VERSION}")
}
```

For static strings, `concat!("ExampleApp ", env!("CARGO_PKG_VERSION"))`
also works. A stable help heading that does not need the release number can
simply omit it. Different packages in a workspace may intentionally have
different package versions; do not manufacture a global version authority.

**Keep independent contracts independent.** A CLI JSON protocol identifier
such as `sample-app.cli/v1`, database schema numbers, wire/API format
versions, explicit supported-version ranges, release-history examples and
historical roadmap milestones have different compatibility or documentary
meaning. They must **not** be replaced with the Cargo release version or
automatically advanced on every release.

### Reviewer check

- Is the string actually meant to display the *current built package version*?
  If so, does it read the same release authority as the build instead of a
  second manually maintained literal?
- Would a package version change update normal `--version` output without
  searching unrelated source files?
- Are independent compatibility/schema IDs intentionally unchanged and tested?
- Is a proposed version helper necessary, or would the existing package
  metadata (or no banner version at all) be simpler?

This is guidance, **not** a requirement to build a version registry, rewrite
old documentation, change independent schema versions, or change a package's
release/merge approval procedure.

[Back to standards index](../standards.md).
