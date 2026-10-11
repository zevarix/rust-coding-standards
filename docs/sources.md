# Sources and attribution

This repository is **independently authored guidance**, not a copy of the materials below. The links inform the intent of individual rules; the linked sources retain their own copyright, licensing, stability and maintenance status.

| Source | Role in this draft |
| --- | --- |
| [The Rust Style Guide](https://doc.rust-lang.org/style-guide/) | Formatting principles; use the default `rustfmt` style |
| [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) | Naming, predictable public API design, useful newtypes, documentation and error types |
| [The Rust Programming Language](https://doc.rust-lang.org/book/) | Idiomatic ownership, errors, testing and application-level explanations |
| [Clippy documentation](https://doc.rust-lang.org/clippy/) | Mechanical diagnostics and selectable lint categories |
| [Cargo Book](https://doc.rust-lang.org/cargo/) | Workspace/toolchain/dependency workflow context |
| [Safety-Critical Rust Consortium](https://arewesafetycriticalyet.org/) | Research reference for stronger assurance when justified |
| [Consortium coding guidelines](https://coding-guidelines.arewesafetycriticalyet.org/) | Emerging/draft suggestions to evaluate case-by-case, **not** automatically adopted standards |


## Rustacean mascot inspiration and original artwork

[Ferris the Crab](https://rustacean.net/) is the **unofficial** Rust mascot
created by Karen Rustad Tölva. The website publishes a copyright waiver
for Ferris artwork. We use Ferris as a cultural reference only: the
hexagonal crab mark in this repository was **drawn independently**,
not copied from Ferris's offered SVG/PNG files. No sponsorship or
endorsement by the Rust Project or mascot artist is implied.

The guidelines' mark and visual style remain **unreleased private draft assets**;
an eventual original-document/artwork license and public-use review are still
owner-controlled decisions.


## Source handling

- Link to upstream explanations rather than reproducing their prose or examples verbatim.
- Mark independently authored rules as our own; don't call them official Rust policy.
- An upstream checklist item does **not** imply universal applicability to application internals. Consider whether the source describes public libraries, formatting, tooling or a specific assurance domain.
- Before public release, verify licensing of all included material, select a license for original text, and perform a private-information and provenance check.
- Upstream links can change. Review cited upstream semantics when materially revising a rule; do not silently import new upstream requirements.

## First publication decision still pending

**No documentation license has been selected and no public release is authorized.** The repository owner will explicitly choose a license and approve visibility changes after reviewing the draft. Avoid third-party pasted guideline text or examples until redistribution rights have been examined.
