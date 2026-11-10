# Contributing to Rust Coding Standards

Thank you for helping improve these independently authored Rust guidelines. The
project is a working draft: a proposed rule should make Rust easier to read,
test or maintain, not merely add another reviewer requirement.

Start with the [full contribution guide](docs/contributing.md), the
[standards index](docs/standards.md), and the [review guide](docs/review-guide.md).
For a substantive rule change, open a focused GitHub issue describing the
specific problem, applicability, exceptions and verification evidence, then
propose a reviewable pull request. Keep rule IDs stable when possible.

## Questions, ideas, and reports

- Ask about rules, adoption, or skills in [Discussions Q&A](https://github.com/zevarix/rust-coding-standards/discussions/categories/q-a).
- Explore early suggestions in [Ideas](https://github.com/zevarix/rust-coding-standards/discussions/categories/ideas).
- Use the [issue chooser](https://github.com/zevarix/rust-coding-standards/issues/new/choose) for concrete rule proposals or RCS documentation, example, and tooling defects.
- Report security-sensitive defects through [private vulnerability reporting](https://github.com/zevarix/rust-coding-standards/security/advisories/new), following [SECURITY.md](SECURITY.md).

Discussions help develop a proposal; scoped implementation work belongs in an
issue and pull request. Keep public examples synthetic and sanitize any logs.

## Validate your change

Follow the [environment setup and validation commands](docs/site-preview.md#check-documentation-and-rust-examples)
for Windows PowerShell or macOS/Linux. They check source links and rule IDs,
build the documentation, inspect rendered output, run the Python tests, and
compile/run marked Rust examples. The example check requires a Rust toolchain
supporting edition 2024.

CI builds documentation and runs tagged, self-contained Rust examples; it does
not deploy the website. The consuming project chooses its own Rust toolchain,
tests, architecture and merge authority.

## Copyright and contributor rights

**Copyright (c) 2026 Peder Klockmann (Zevarix)** for original project content.
Contributors retain copyright in their contributions. Unless a different
arrangement is clearly recorded and accepted, original contributions to the
standards, examples, validators or independent Forge crab SVG are offered
under **MIT OR Apache-2.0**, at the recipient's choice.

The original Forge CSS and custom homepage presentation are **all rights
reserved** and excluded from those open licenses. Changes to these files
need separate coordination with their owner. See
[Licensing and reuse](docs/licensing.md) and [LICENSE-FORGE-THEME](LICENSE-FORGE-THEME).

Respect third-party copyrights and trademarks: cite references, do not paste
proprietary examples, external artwork, secret credentials, private project
payloads or someone else's documentation into a contribution. This repository
is **not affiliated with or endorsed by** the Rust Project or Rust Foundation.

For a confidential vulnerability report, follow [SECURITY.md](SECURITY.md)
rather than posting sensitive details in a public issue.
