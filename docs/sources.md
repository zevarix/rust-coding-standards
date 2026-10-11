# Sources and attribution

This repository is **independently authored guidance**, not a copy of the materials below. The links inform the intent of individual rules; the linked sources retain their own copyright, licensing, stability and maintenance status.

| Source | Role in this draft |
| --- | --- |
| [The Rust Style Guide](https://doc.rust-lang.org/style-guide/) | Formatting principles; use the default `rustfmt` style |
| [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) | Naming, predictable public API design, useful newtypes, documentation and error types |
| [The Rust Programming Language](https://doc.rust-lang.org/book/) | Idiomatic ownership, errors, testing and application-level explanations |
| [Clippy documentation](https://doc.rust-lang.org/clippy/) | Mechanical diagnostics and selectable lint categories |
| [Cargo Book](https://doc.rust-lang.org/cargo/) | Workspace/toolchain/dependency workflow context |
| [Standard checked integer arithmetic](https://doc.rust-lang.org/std/primitive.u64.html#method.checked_add) | Bounded arithmetic when overflow is invalid |
| [`TryFrom` conversions](https://doc.rust-lang.org/std/convert/trait.TryFrom.html) | Fallible, lossless numeric and type conversions |
| [`OpenOptions::create_new`](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html#method.create_new) | Atomic exclusive file creation within a larger application safety contract |
| [Rust `Read`](https://doc.rust-lang.org/std/io/trait.Read.html) | Streaming/bounded input observations |
| [SQLite transaction control](https://www.sqlite.org/lang_transaction.html) | Atomic writes and writer reservation |
| [SQLite PRAGMAs](https://www.sqlite.org/pragma.html) and [schema table](https://www.sqlite.org/schematab.html) | Live recovered schema and foreign-key integrity |
| [Rust `std::path`](https://doc.rust-lang.org/std/path/) | Native pathname representation and components |
| [Rust `Command`](https://doc.rust-lang.org/std/process/struct.Command.html) and [`Child`](https://doc.rust-lang.org/std/process/struct.Child.html) | Structured process execution and process lifecycle |
| [Rust atomic types](https://doc.rust-lang.org/std/sync/atomic/) | Explicit shared-memory synchronization primitives |
| [Rust 2024 formatting style edition](https://doc.rust-lang.org/edition-guide/rust-2024/rustfmt-style-edition.html) | Keep Cargo, editor and CI formatting aligned |
| [Cargo testing](https://doc.rust-lang.org/cargo/commands/cargo-test.html) | Actual test targets and feature invocation |
| [Safety-Critical Rust Consortium](https://arewesafetycriticalyet.org/) | Research reference for stronger assurance when justified |
| [Consortium coding guidelines](https://coding-guidelines.arewesafetycriticalyet.org/) | Emerging/draft suggestions to evaluate case-by-case, **not** automatically adopted standards |


## Rustacean mascot inspiration and original artwork

[Ferris the Crab](https://rustacean.net/) is the **unofficial** Rust mascot
created by Karen Rustad Tölva. The website publishes a copyright waiver
for Ferris artwork. We use Ferris as a cultural reference only: the
hexagonal crab mark in this repository was **drawn independently**,
not copied from Ferris's offered SVG/PNG files. No sponsorship or
endorsement by the Rust Project or mascot artist is implied.

The original crab SVG is Copyright (c) 2026 Peder Klockmann (Zevarix), licensed **MIT OR Apache-2.0** alongside the rulebook and tools. The separate Forge CSS and custom homepage visual theme remain **all rights reserved**; see [Licensing and reuse](licensing.md). Licensing alone does not authorize publication; the repository was private at the preparation audit. See the [public-readiness checklist](publication-readiness.md).


## Source handling

- Link to upstream explanations rather than reproducing their prose or examples verbatim.
- Mark independently authored rules as our own; don't call them official Rust policy.
- An upstream checklist item does **not** imply universal applicability to application internals. Consider whether the source describes public libraries, formatting, tooling or a specific assurance domain.
- Before public release, verify the selected [licenses and exceptions](licensing.md) against included material, and perform a private-information and provenance check.
- Upstream links can change. Review cited upstream semantics when materially revising a rule; do not silently import new upstream requirements.

## Publication decision still pending

**The owner has selected MIT OR Apache-2.0 for original RCS documentation, tools and Forge crab SVG, with Forge CSS/homepage theme rights reserved. No public release or visibility change has been authorized.** Review history, assets and third-party materials before future publication, and avoid pasted guideline text/examples without verified redistribution rights.
