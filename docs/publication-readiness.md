# Public repository readiness

This document prepares the repository for a **future, separately authorized**
public visibility decision. It is **not** a publication approval, a deployment
plan that executes by itself, or a statement that GitHub visibility is public.

## Current publication boundaries

At the 2026-10-11 preparation audit, `zevarix/rust-coding-standards` remained
**private**. It had one advertised remote branch (`main`), no release tags,
no releases and no configured GitHub Pages deployment. Its existing workflow
checks source, documentation and Rust examples only. GitHub's present settings
and source history always outrank this dated observation.

The project is independently authored, not an official Rust standard and not
endorsed by the Rust Project or Rust Foundation. Its original rules, examples,
validators and crab SVG are **MIT OR Apache-2.0** (at the user's option);
**Forge CSS and original homepage presentation are rights reserved**. See
[Licensing and reuse](licensing.md). Publishing repository source would make
those reserved-theme files visible in forks and source views, even though
reusing them outside the licensed original site remains restricted.
Copyright restriction does **not** guarantee secrecy.

## Historical exposure review

The preparation audit inspected the current tracked tree and full reachable
`main` history, historical PR HEAD snapshots and patches, issue/PR bodies,
available comment/review discussions and repository metadata. No recognizable
access-token/private-key pattern was found **in those inspected surfaces**.
This is an evidence-based scan, not a guarantee that an unknown secret cannot
exist elsewhere, including deleted objects, attachment content, organization
settings, unlisted GitHub features or external services.

In the audited snapshot, GitHub exposed one branch, eight mainline commits,
seven historical PR HEADs, 15 issue/PR bodies and 25 ordinary issue comments;
no tags, releases or inline review submissions were found. Historical GitHub
conversations include a past Windows workspace path and
some references to private Zevarix projects. These are **not proven credentials**,
but they would become visible in a public repository. The audit deliberately
does not reproduce their exact values here. Historical issue/PR discussion and
past commits may remain accessible after a HEAD edit; editing a GitHub comment
is not necessarily sufficient to erase its edit history.

Review and explicitly accept or remediate these residual disclosures at the
**actual visibility-change decision**, using current live GitHub records.
Never rewrite or delete Git history or GitHub conversations merely to make an
audit report look clean without separately authorized retention decisions.

## 2026-11-08 current-surface reconciliation

Following owner direction, the source's former named-consumer references have
been generalized in the README, Forge homepage copy, one rule example and its
regression test. The site's visual theme and rule semantics remain unchanged.

The current GitHub issue and pull-request descriptions were inspected and 14
affected descriptions edited. Three top-level issue/PR comments were edited to
remove named private consumers or machine-specific checkout paths. Independent
API readback verified each affected item; a fresh scan of all 23 issue/PR
descriptions and 29 issue/PR comments found no remaining matches for the
targeted private-project references or personal workspace paths.

The owner accepted leaving residual provenance in historical records instead of
rewriting Git commits or deleting GitHub discussions. **These edits do not
erase** historical commit contents, GitHub edit history, API caches, attachments,
previously shared URLs, or unexamined external copies. Rerun a full final
exposure review immediately before any public visibility change. This work
does not authorize publication, license changes or theme distribution.

## Final owner-controlled exposure checklist

- [ ] Recheck the repository's **live** GitHub visibility, branch, refs, issues,
      PRs, comments, releases, actions and any attached assets. Rerun the
      source/history exposure review on the exact final state.
- [ ] Explicitly accept or separately remediate the historical local path and
      private-project references, with awareness that prior revisions may
      remain visible.
- [ ] Confirm permission to show the original Forge CSS/homepage sources
      publicly under their separate **all-rights-reserved** notice; public
      source visibility is **not** an MIT/Apache license for that theme.
- [ ] Verify all tracked sources, code examples, SVG artwork and citations
      have appropriate provenance and redistribution rights; do not copy
      unlicensed third-party assets or disclose consumer data.
- [ ] Recheck the canonical **MIT OR Apache-2.0** dual-license texts,
      `COPYRIGHT`, `NOTICE`, reserved-theme exception and owner attribution.
- [ ] Verify source-only CI, rendered Markdown, links, executable Rust examples
      and required tests on the final main commit. Distinguish hosted CI
      success from manual external-link or legal review.
- [ ] Make a separate decision about branch protection/rulesets,
      vulnerability-reporting features and other GitHub **settings**;
      none is changed by this preparation work.
- [ ] Obtain Peder's explicit authorization for **private → public**
      repository visibility. Perform only that authorized change, then
      independently read back visibility, public source access, licensing,
      repository links and CI behavior.
- [ ] Treat hosting the rendered documentation, a public domain, release
      tag, versioned publication, or other distribution as **separate**
      decisions. GitHub public visibility alone does not deploy Zensical.

The applicable instructions are the [contribution guide](https://github.com/zevarix/rust-coding-standards/blob/main/CONTRIBUTING.md)
and [security policy](https://github.com/zevarix/rust-coding-standards/blob/main/SECURITY.md). Recheck this document against live
GitHub state before treating any box as completed. No action in this runbook
automatically changes visibility.
