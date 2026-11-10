# Zevarix Rust Coding Standards

**Working draft — no versioned release yet.**

Reusable, explicit Rust engineering standards for Zevarix projects, with rule identifiers, rationale, examples and review guidance.

## Quickstart

For a code review, open the [standards index](docs/standards.md) and follow the
[review guide](docs/review-guide.md) to select the rules relevant to your change.

To install the two Rust skills, run this from the project that should receive
them, using Node.js/npm supported by the [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md):

```sh
npx skills add zevarix/rust-coding-standards --skill rcs-guidance rust-performance --agent codex --copy
```

This example installs project-local copies for Codex. Review the installer's
destination before replacing any existing skills. See the [skills guide](docs/skills.md)
for other clients, authentication, updates and fixed-revision installs.
Once your client discovers the skills, try:

```text
Use $rcs-guidance to review this Rust change against the applicable RCS rules.
Use $rust-performance to investigate this slow operation and compare optimizations.
```

Installing a skill does not adopt standards for your repository. Use the
[adoption guide](docs/adoption.md) to declare scope and choose latest `main`
or a fixed revision.

## Documentation

- [Documentation website](https://rcs.zevarix.com/)
- [Documentation home](docs/index.md)
- [Standards index](docs/standards.md)
- [Installable Rust skills](docs/skills.md)
- [Source references](docs/sources.md)
- [How projects adopt these guidelines](docs/adoption.md)
- [Preview and build instructions](docs/site-preview.md)
- [Contributing](CONTRIBUTING.md) and [security reporting](SECURITY.md)
- [Community questions and ideas](https://github.com/zevarix/rust-coding-standards/discussions)
- [Public-readiness review and publication checklist](docs/publication-readiness.md)

The site is built with **Zensical** from the Markdown in `docs/`. GitHub Pages publishes validated updates from `main`; pull requests run checks only. See the [preview instructions](docs/site-preview.md) to build and browse the site locally.

**Licensing:** Original RCS rules, documentation, examples, validation tools and [Forge crab SVG](docs/assets/brand/forge-crab.svg) are offered under **MIT OR Apache-2.0**, at your choice, with copyright attributed to **Peder Klockmann (Zevarix)**. The original **Forge CSS and homepage visual theme** are **all rights reserved** and excluded from those licenses. See [Licensing and reuse](docs/licensing.md), [COPYRIGHT](COPYRIGHT), [LICENSE-MIT](LICENSE-MIT), [LICENSE-APACHE](LICENSE-APACHE) and [LICENSE-FORGE-THEME](LICENSE-FORGE-THEME).
