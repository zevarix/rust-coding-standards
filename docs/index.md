---
title: Rust Coding Standards for Humans and AI Agents
description: Rust coding standards for correct, fast, maintainable software. Rules for human developers and AI coding agents covering performance, testing, and safety.
---

<!-- Copyright (c) 2026 Peder Klockmann (Zevarix). Original Forge homepage presentation: all rights reserved. See LICENSE-FORGE-THEME at repository root. Links and headings work without JavaScript. -->

<div class="forge-home">
  <section class="forge-hero" aria-labelledby="forge-hero-title">
    <div class="forge-hero__copy">
      <h1 id="forge-hero-title">Rust coding standards</h1>
      <p class="forge-hero__lead">Conventions for naming, APIs, errors, unsafe code, performance, and testing. Each rule explains when it applies, includes examples, and states how to check it.</p>
      <div class="forge-actions">
        <a class="forge-button forge-button--accent" href="standards/">Browse rules</a>
        <a class="forge-button forge-button--quiet" href="adoption/">Adoption guide</a>
      </div>
      <p class="forge-hero__foot">Working draft · Project-local adoption</p>
    </div>
    <div class="forge-window" aria-label="Example Rust function using checked arithmetic">
      <div class="forge-window__bar">
        <span class="forge-window__file"><span class="forge-lights" aria-hidden="true"><b></b><b></b><b></b></span> example.rs</span>
        <span>Rust</span>
      </div>
      <pre><code><span class="forge-comment">// Sum without wrapping on overflow.</span>
<span class="forge-keyword">fn</span> <span class="forge-function">checked_total</span>(
    parts: &amp;[u64],
) -&gt; Option&lt;u64&gt; {
    parts.<span class="forge-function">iter</span>().<span class="forge-function">try_fold</span>(
        0,
        |sum, value| {
            sum.<span class="forge-function">checked_add</span>(*value)
        },
    )
}</code></pre>
      <div class="forge-window__foot">Example: checked arithmetic</div>
    </div>
  </section>

  <section class="forge-intro" aria-labelledby="explore-by-topic">
    <h2 id="explore-by-topic">Rules by topic</h2>
    <p>Choose a subject below, <a href="topics/">browse all topics</a>, or use search to find a specific rule ID.</p>
  </section>
  <section class="forge-intro" aria-labelledby="ai-rust-quality">
    <h2 id="ai-rust-quality">Write better Rust, whether you're a human or an AI agent</h2>
    <p>RCS treats correctness, runtime efficiency, and maintainability as design concerns from the start. Follow evidence-backed rules, review costly repeated work across call paths, and validate meaningful behavior rather than trusting a green test count.</p>
    <p>Want to avoid AI-generated boilerplate and over-defensive code? Read our <a href="ai-rust-code-quality/">Anti-AI-Slop Rust guide</a> for concrete review questions, safe optimization boundaries, and checks that apply equally to human-written code.</p>
  </section>
  <div class="forge-grid">
    <a class="forge-card" href="rules/style-and-structure/">
      <span class="forge-card__title">Formatting and modules</span>
      <span class="forge-card__description">rustfmt, naming, and module responsibilities.</span>
    </a>
    <a class="forge-card" href="rules/types-and-errors/">
      <span class="forge-card__title">Types, APIs, and errors</span>
      <span class="forge-card__description">Distinct identities, conventional interfaces, and explicit failures.</span>
    </a>
    <a class="forge-card" href="rules/safety/">
      <span class="forge-card__title">Unsafe code and user data</span>
      <span class="forge-card__description">Unsafe contracts, file ownership, and non-destructive defaults.</span>
    </a>
    <a class="forge-card" href="rules/performance/">
      <span class="forge-card__title">Performance</span>
      <span class="forge-card__description">Whole-call-path costs, redundant work, and evidence for optimizations.</span>
    </a>
    <a class="forge-card" href="rules/testing/">
      <span class="forge-card__title">Testing and documentation</span>
      <span class="forge-card__description">Deterministic fixtures, failure cases, and documented contracts.</span>
    </a>
  </div>
</div>

## How to use these guidelines

The rules draw on the Rust Style Guide, Rust API Guidelines, and Clippy. Every rule specifies whether it is required or advisory, where it applies, and how to evaluate it. See the [standards index](standards.md) or [source references](sources.md).

## Rust coding standards: common questions

### What do Rust coding standards add beyond rustfmt and Clippy?

[rustfmt](https://github.com/rust-lang/rustfmt) handles formatting, while [Clippy](https://github.com/rust-lang/rust-clippy) detects many mechanical mistakes and suspicious patterns. RCS complements those tools with reviewable behavioral and engineering questions: are important state transitions correct, are errors recoverable, does an operation repeat expensive work, and do the tests prove the claimed behavior? Start with the [indexed RCS rules](standards.md) and apply only the rules relevant to the change.

### How does RCS help produce faster Rust code?

Performance should be considered during design, not only after users report slow operations. [RCS-PERF-001](rules/performance.md#rcs-perf-001--review-work-across-call-paths) asks reviewers to count the *whole call path's* expensive operations—database queries, parsing, allocation, native calls and large file reads—rather than judging one helper in isolation. The [performance workflow](performance/optimization.md) then measures candidates on comparable workloads while protecting correctness and recovery boundaries.

### Can AI coding agents apply the same standards as human developers?

Yes. The standard applies based on the consuming project's declared scope, independent of who authored the code. [RCS guidance and Rust performance skills](skills.md) help an agent retrieve the current rulebook and investigate bottlenecks; those skills do not override a project's safety requirements or grant merge authority. For practical review of unnecessary abstraction and redundant checks, read [Anti AI Slop Rust](ai-rust-code-quality.md).

### May tests change when Rust implementation changes?

Absolutely. Legitimate behavior or interface changes often require tests to evolve. The constraint is **not** to weaken independent correctness evidence merely to make a performance experiment appear successful. See [risk-weighted behavioral verification](verification/assurance.md) for positive and negative cases, test effectiveness, and scope-appropriate tools.

### Does RCS replace official Rust guidance?

No. It builds on the [Rust Style Guide](https://doc.rust-lang.org/style-guide/), Rust API Guidelines, and standard Rust tooling. It adds scoped rules for consequential applications and specific review guidance for performance, data safety, testing, and maintenance. Adopting projects retain their own requirements and exceptions under the [adoption model](adoption.md).

## Adoption and publication

Use the [adoption guide](adoption.md) to choose latest `main` or a fixed revision and record which rules apply to your project. To propose a change, see [contributing](contributing.md).

Original RCS guidelines, code examples and the Forge crab mark are **MIT OR Apache-2.0**, Copyright (c) 2026 Peder Klockmann (Zevarix); the authored **Forge CSS and homepage theme** remain rights reserved. See [Licensing and reuse](licensing.md). The crab mark is not official Rust branding.
