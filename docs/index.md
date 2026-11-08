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
    <p>Choose a subject below or use search to find a specific rule ID.</p>
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

## Adoption and publication

Projects explicitly adopt either latest main or a selected revision, and retain their own architecture, exceptions, testing, and merge authority. See [adoption](adoption.md) and [contributing](contributing.md).

Original RCS guidelines, code examples and the Forge crab mark are **MIT OR Apache-2.0**, Copyright (c) 2026 Peder Klockmann (Zevarix); the authored **Forge CSS and homepage theme** remain rights reserved. See [Licensing and reuse](licensing.md). Repository visibility, documentation hosting and public releases are separate owner decisions. RCS licensing does not itself approve publication. The crab mark is not official Rust branding.
