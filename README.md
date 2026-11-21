# Zevarix Rust Coding Standards

**Working draft — no versioned release yet.**

Reusable, explicit Rust engineering standards for Zevarix projects, with rule identifiers, rationale, examples and review guidance.

## What these standards help you build

RCS brings together practical standards for **correct, efficient, maintainable Rust** written by humans or AI coding agents. The rulebook covers explicit errors, realistic failure cases, safe state transitions, and costly repeated work across complete execution paths—not arbitrary source-length or coverage quotas.

For a focused review of generated code, see [Anti AI Slop Rust](https://rcs.zevarix.com/ai-rust-code-quality/). For code that passes tests but runs slowly, start with [performance and execution cost](https://rcs.zevarix.com/rules/performance/) and [the optimization workflow](https://rcs.zevarix.com/performance/optimization/). Browse the [full topic index](https://rcs.zevarix.com/topics/) for related guidelines.

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

## ChatGPT and Codex plugin

The source for the **Rust Coding Standards** skills-only plugin lives in
[plugin/rust-coding-standards/plugin.json](plugin/rust-coding-standards/plugin.json).
Build it directly from the two canonical Rust skills; no copied standards or MCP
server are needed:

```sh
python tools/package_rcs_plugin.py
```

The ZIP is a generated, Git-ignored artifact named for its manifest version.
Run the package tests before private installation or public submission.
Public review, approval and directory publication are separate from the build,
and neither installation nor publication authorizes changes to user projects.
See [plugin packaging and usage](docs/skills.md#openai-plugin-package).

A **separate MCP-backed plugin candidate** lives in
[plugin/rcs-rust-standards](plugin/rcs-rust-standards/README.md). It combines
the same two canonical skills with the real public, read-only RCS MCP tools:

```sh
python tools/package_rcs_mcp_plugin.py
```

This is a reproducible technical **candidate**, not an approved or published
ChatGPT directory plugin. The existing skills-only plugin is unchanged. The
separate MCP-backed draft has verified domain ownership and public privacy and
terms pages, but still requires a real reviewer demonstration, owner attestations,
submission, review and a separately authorized publication step. See
[RCS public plugin review issue #64](https://github.com/zevarix/rust-coding-standards/issues/64).

## Read-only MCP documentation lookup

The **live** [RCS MCP service](mcp/rcs/README.md) provides source-cited,
read-only rule search, exact rule retrieval, review guidance and revision
details to remote MCP clients:

- **MCP endpoint:** https://rcsmcp.zevarix.com/mcp
- **Health and source revision:** https://rcsmcp.zevarix.com/health

The service runs on an existing isolated Hostinger Node.js application. It uses
the same publicly licensed RCS rulebook without a separate hand-maintained
copy, account access, write tools, user files, a database or paid AI inference.
The optional Cloudflare Worker transport is still tested but **undeployed**;
its separate cost and release gate remains in effect. Production deployment and
OpenAI directory publication are independently authorized steps.

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
