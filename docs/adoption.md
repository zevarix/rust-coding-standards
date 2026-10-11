# Adopting the guidelines

Adoption is **explicit and repository-local**. A standards document does not govern a different repository merely because both live under the same account or organization.

## Suggested adopter declaration

Place a short note in the adopting repository's own contributing/development documentation, tailored to that project's authority:

```text
Rust coding guidance:
  Source: zevarix/rust-coding-standards
  Revision: <reviewed immutable commit SHA or released version>
  Scope: new or meaningfully changed Rust code
  Local exceptions: <path to owner-local exceptions, or "none">
  Owner: <owning repository and issue/decision>
```

A project must select a real revision after reviewing it. This draft does **not** supply a release tag. Any source that is still private must only be used by authorized members; copying private text into a public project would itself be a separate publication decision.

## What stays local

- Architecture, filesystem trust and product safety boundaries
- Supported Rust/toolchain versions and operating systems
- Enabled Clippy lints and CI commands
- Whether and how external review is used
- Project-specific exceptions and migration strategy
- PR integration, release, deployment and publication authority

A consumer may adopt a subset or stricter rules, but should identify the difference explicitly rather than pretending every rule applies unchanged.

## Example validation

These are examples, not commands to impose on every repo:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets --all-features
cargo test --all-targets --all-features
```

For an application that commits `Cargo.lock`, a project may add `--locked`. For crates with non-default platform features or specialized test harnesses, select the appropriate subset and describe what was actually checked. Do not claim a test passed because another project's check passed.

## Upgrades

Propose an adoption update as an owner-reviewed PR: compare the old pinned revision to the proposed one, test affected code, document newly adopted or excepted rules, and obtain the project's normal merge authority. An external standards update never automatically changes existing consumer policy.
