# Reusable Rust skills

RCS standards state engineering expectations. RCS skills provide practical
workflows for applying that guidance; they do not introduce another rule
level, grant mutation authority or replace a consuming project's contracts.

| Skill | Load for |
| --- | --- |
| [rust-performance](https://github.com/zevarix/rust-coding-standards/blob/main/skills/rust-performance/SKILL.md) | Slow Rust operations, worker scaling, performance comparisons, allocation/memory/I/O costs, binary size or build time |

## Use a skill

Read the skill from current RCS `main`, then load only the references needed
for the task. Record the actual RCS revision inspected in implementation or
review evidence, following [adoption guidance](adoption.md).

The canonical directory is `skills/rust-performance/`. To use an agent's
local skill discovery, deliberately install the complete directory, including
its references and metadata, in that client's documented skill location.
This repository does not automatically install skills or change an agent's
configuration. A consuming project may instead link to the canonical source
and instruct agents to read it when applicable.

Keep host details, private datasets, raw profiles and project-specific
decisions with the consuming project. Add only generalized methods and
redistributable examples here. Skills use this repository's open
[licensing scope](licensing.md); theme exceptions remain separate.
