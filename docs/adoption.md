# Adopting the guidelines

Each project adopts RCS by adding a declaration to its own documentation.

## Suggested adopter declaration

Add a note to the project's contributing or development guide:

```text
Rust coding guidance:
  Source: zevarix/rust-coding-standards
  Standards reference: main (latest at time of implementation/review)
  Scope: new or meaningfully changed Rust code
  Local exceptions: <path to owner-local exceptions, or "none">
  Owner: <owning repository and issue/decision>
```

Projects following `main` read the current guidance during implementation and
review, then record the **RCS commit consulted** in their PR or review evidence.
That record identifies the rules used; the project does not need to maintain a
commit pin. Choose a fixed commit when a project needs one for a specific
assurance requirement. RCS has no release tag yet.

## What stays local

- Architecture, filesystem trust and product safety boundaries
- Supported Rust/toolchain versions and operating systems
- Enabled Clippy lints and CI commands
- Whether and how external review is used
- Project-specific exceptions and migration strategy
- PR integration, release, deployment and publication authority

List any rules you omit or tighten in the adoption declaration.

## Use in a review skill

Tell implementers and reviewers to consult the adopted revision and cite
applicable `RCS-*` IDs with their findings. The [reviewer guide](review-guide.md)
provides a method and an example comment. Link to the rulebook rather than
copying it into each project or automatically mirroring content when `main`
advances.

Example review instruction:

```text
When reviewing changed Rust, read the owning issue and local safety contracts first.
Then inspect applicable rules from the explicitly adopted RCS revision.
Cite rule IDs only for demonstrated applicability and evidence-backed findings.
A clean RCS assessment is not independent review or merge authorization.
```

Use private project source only with its normal access permissions. Follow the
[publication checklist](publication-readiness.md) before copying private
material into public documentation.

## Example validation

These are examples, not commands to impose on every repo:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets --all-features
cargo test --all-targets --all-features
```

For an application that commits `Cargo.lock`, a project may add `--locked`. For crates with non-default platform features or specialized test harnesses, select the appropriate subset and describe what was actually checked. Do not claim a test passed because another project's check passed.

## Upgrades

Projects following `main` do not need a PR just to refresh a rulebook SHA.
Record the revision used for new work; past accepted changes keep their
original review record. Projects using a fixed commit update it through their
normal review process.

RCS updates do not automatically change a project's code or policy. Make those
changes through the project's issue, PR, testing and approval process.
