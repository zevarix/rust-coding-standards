# Adopting the guidelines

Adoption is **explicit and repository-local**. A standards document does not govern a different repository merely because both live under the same account or organization.

## Suggested adopter declaration

Place a short note in the adopting repository's own contributing/development documentation, tailored to that project's authority:

```text
Rust coding guidance:
  Source: zevarix/rust-coding-standards
  Standards reference: main (latest at time of implementation/review)
  Scope: new or meaningfully changed Rust code
  Local exceptions: <path to owner-local exceptions, or "none">
  Owner: <owning repository and issue/decision>
```

With `main` adoption, no recurring revision bump is required. Human/agent coders and reviewers read the current guidance when they work, and record the **actual RCS commit SHA consulted** in the relevant PR/review evidence. That SHA is historical provenance, **not** a pin in the consumer's governance files. A project may deliberately choose an immutable commit or release for a specific assurance need; this remains optional. The repository currently has no release tag. Private material is only accessible to authorized members; copying private text to a public repository is a separate publication decision.

## What stays local

- Architecture, filesystem trust and product safety boundaries
- Supported Rust/toolchain versions and operating systems
- Enabled Clippy lints and CI commands
- Whether and how external review is used
- Project-specific exceptions and migration strategy
- PR integration, release, deployment and publication authority

A consumer may adopt a subset or stricter rules, but should identify the difference explicitly rather than pretending every rule applies unchanged.

## Use in a review skill

An adopting repository may tell implementers **and** reviewers to read the applicable rules from current `main` and cite relevant `RCS-*` IDs in evidence-backed findings. The [reviewer guide](review-guide.md) defines a concise method and an example comment. Do **not** paste the whole rulebook into each project or automatically mirror standards content/code when `main` advances.

A workable, owner-local review instruction would be:

```text
When reviewing changed Rust, read the owning issue and local safety contracts first.
Then inspect applicable rules from the explicitly adopted RCS revision.
Cite rule IDs only for demonstrated applicability and evidence-backed findings.
A clean RCS assessment is not independent review or merge authorization.
```

Any private repository source remains subject to the consumer's actual access permissions. The initial draft is not yet a released standard; adopters must not assume an unapproved commit pin.

## Example validation

These are examples, not commands to impose on every repo:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets --all-features
cargo test --all-targets --all-features
```

For an application that commits `Cargo.lock`, a project may add `--locked`. For crates with non-default platform features or specialized test harnesses, select the appropriate subset and describe what was actually checked. Do not claim a test passed because another project's check passed.

## Upgrades

For projects following latest `main`, **no project PR is necessary merely to refresh a rulebook SHA**. New work and reviews consult current applicable rules and record the revision inspected, while past accepted changes remain historical. A substantive local code, safety-contract or policy change still follows the consuming repository's own issue/PR, tests and owner authority. A project that deliberately uses an immutable pin may update it through its own established review process. External guideline updates never grant authority to rewrite, merge, deploy or publish consumer work.
