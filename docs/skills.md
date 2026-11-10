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
