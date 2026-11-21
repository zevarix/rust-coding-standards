---
title: "Rust AI Coding Agent Skills: Code Review and Performance"
description: "Install Rust coding agent skills for reviewing changes, measuring performance, and applying the RCS rules without inventing extra approval requirements."
tags:
  - AI-assisted Development
  - Tooling
  - Performance
---

# Reusable Rust skills

RCS documentation is the canonical source of standards and technical guidance.
Skills are small task workflows that find and apply that documentation.
They do not add a rule level or grant mutation, merge or publication authority.

| Skill | Load for |
| --- | --- |
| [rcs-guidance](https://github.com/zevarix/rust-coding-standards/blob/main/skills/rcs-guidance/SKILL.md) | Find applicable RCS standards, adoption and implementation/review guidance |
| [rust-performance](https://github.com/zevarix/rust-coding-standards/blob/main/skills/rust-performance/SKILL.md) | Investigate slow Rust operations and compare optimization experiments |

Detailed methods live in the [measurement](performance/measurement.md),
[profiling](performance/profiling.md) and
[optimization](performance/optimization.md) documentation. Skills load these
pages as needed rather than carrying separate copies.

When reviewing generated code, follow the [Anti AI Slop Rust guide](ai-rust-code-quality.md) to examine behavioral correctness, performance and unnecessary complexity.

## OpenAI plugin package

RCS also offers a **skills-only plugin** for ChatGPT and Codex that installs the
same `rcs-guidance` and `rust-performance` workflows as one bundle. The
manifest is stored under `plugin/rust-coding-standards/plugin.json`, and the
package builder reads the *current repository skill files* when invoked:

```sh
python tools/package_rcs_plugin.py
python -m unittest discover -s tools -p "test_*.py"
```

The generated, version-named ZIP contains the plugin manifest, the original
two complete skill directories including their license notices, and the
openly licensed 512 x 512 PNG rendition of the Forge crab icon. It contains
**no MCP server or live document snapshot**. The skills still resolve the adopting project's chosen RCS revision and read
the relevant current documentation from a permitted source. They do not
implicitly gain file, network or repository-writing permissions.

The ZIP is deliberately Git-ignored. Test it privately first. Public
directory submission requires a verified individual or business identity,
passing skill scans and owner-completed attestations. An uploaded draft is
not an approved or published directory listing. The plugin's bundled
skills share this repository's normal MIT OR Apache-2.0 material, not the
rights-reserved Forge website CSS.

After successful validation on `main`, GitHub Actions attaches the generated
ZIP as the `rcs-plugin` artifact for that exact workflow run. Download and
extract the Actions artifact to obtain the **inner**, version-named
`rcs-plugin-<version>.zip` for a directory submission. The Actions artifact
wrapper is not itself the OpenAI plugin package. A downloadable ZIP does not
mean the plugin was submitted, approved, or published.

## Read-only MCP rule retrieval (development)

The [RCS MCP server source](https://github.com/zevarix/rust-coding-standards/tree/main/mcp/rcs)
provides a separate public-documentation interface using the Streamable HTTP
protocol. Its tools search exact rule IDs and topics, return the full sourced
rule, expose review/performance guidance, and report the exact Git revision.

The server does not accept or store private repository content and cannot
modify a project. It is **not yet hosted**. Its build/test workflow and
deployment cost gate are documented with its source. The existing skills-only
OpenAI plugin is a separate package and is not automatically converted to an
MCP-backed plugin by this work.

## Install with the Skills CLI

Run installation from the project that should receive the skills. Use a
Node.js version supported by the selected
[Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

List the repository's skills without installing:

```sh
npx skills add zevarix/rust-coding-standards --list
```

Install either skill, or select both. This example targets Codex in the
current project and copies the complete skill packages:

```sh
npx skills add zevarix/rust-coding-standards --skill rcs-guidance rust-performance --agent codex --copy
```

Select another supported client with `--agent`; inspect the CLI's current
help for available targets. Project installation is the default. Add
`--global` only when deliberately choosing a user-wide installation. The
installer may replace an existing same-name skill; review the destination
and preserve local changes before reinstalling.

Each skill directory includes `SKILL.md`, client metadata, both complete
license texts and its attribution notice. Detailed RCS documentation is
loaded through an authorized GitHub route or an existing RCS checkout at the
consumer's selected revision.

If the selected source requires authentication, use existing authorized
repository access. The CLI supports configured Git/GitHub CLI/SSH
authentication; do not put credentials in commands or repository files.
This installation guide does not change visibility or publish a package.

## Check and update installed workflows

From the same project:

```sh
npx skills list
npx skills check --project
npx skills update --project rcs-guidance rust-performance
```

The check command exits with status 1 when an update is available. Review
updates before applying them; use `--global` for a deliberately global
installation. CLI commands can evolve, so verify the selected version's help.

Manual copies and local-directory installs may not be tracked as updatable
remote sources. In the tested CLI 1.7.6, project check/update skips local-directory
installs even when `skills list` shows them. A "no updates" result does not prove
those copies are current: compare them with the intended source revision and
reinstall deliberately, preserving any local changes first.

For a reproducible skill-source revision, the tested CLI 1.7.6 accepts
`zevarix/rust-coding-standards#<git-ref>`; replace the placeholder with an
intentional full commit or tag and quote the source argument. In that
version, `@` selects a skill rather than pinning a Git revision. Verify the
selected CLI version's syntax and inspect the generated lock/provenance
files; a successful exit alone does not prove the requested source ran.
Alternatively, check out the desired revision in an RCS clone, verify its
HEAD, and pass that local directory to `skills add`. RCS has no versioned
release to imply by these examples.

Updating an installed workflow and selecting the documentation revision are
different choices. A project adopting latest RCS `main` still resolves and
records current documentation when working. A project adopting a fixed
revision continues using that revision. Installing a skill does not change
either declaration; see [adoption](adoption.md).

## Direct use and portability

A project may link to canonical skill source and instruct an agent to read it.
Alternatively, copy the entire `skills/rcs-guidance/` or
`skills/rust-performance/` directory into the client's documented skill
location, preserving metadata, notices and licenses. Client discovery and
invocation behavior vary; the standard directory is not an automatic
installation into every application.

Keep machine details, private datasets, raw profiles and project decisions
with the consuming project. Shared RCS additions use generalized methods and
redistributable examples. See [licensing and reuse](licensing.md).
