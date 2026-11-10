# Publication readiness

Use this checklist when preparing source, a documentation site or a versioned
release. Public visibility, hosting and releases are **separately authorized**
owner decisions. This checklist does not itself authorize any of them.

## Source and repository identity

Keep the repository's canonical address and existing adoption/skill links
consistent. Review every tracked file selected for publication, including
examples, configuration, SVG metadata, contributor guidance and notices.

Remove credentials, personal workspace paths, internal host/network details,
consumer data and unnecessary references to private projects. Use generic
examples when a consumer's identity is irrelevant. Keep technical decisions,
legitimate authorship and required attribution.

## Historical and GitHub exposure

Cleaning current files does not clean historical records. Before changing
visibility, inspect:

- all advertised branches/tags and reachable commits;
- historical pull-request heads, diffs, bodies and review comments;
- issue/comment bodies and available edit history;
- Actions history, logs, artifacts, releases and attached assets;
- repository descriptions, homepage links and relevant settings.

Run secret scanning and a separate private-information review. Record the exact
coverage, unavailable surfaces and limitations. A scanner's zero findings do
not prove that every type of sensitive information is absent.

Classify each remaining disclosure and let the owner explicitly accept or
remediate it before publication. References to another project or a local
path are not automatically credentials, but they still need a deliberate
exposure decision. Ordinary edits may leave older versions reachable.

Prepare any proposed history rewrite separately. Identify the exact material,
affected refs and pull requests, required backups, clone reconciliation and
retained GitHub references/caches. Do not rewrite commits, delete discussions,
remove Actions evidence or change protections just to make a scan look clean.
Such effects need their own authority and readback.

Keep detailed private findings and temporary audit artifacts outside the
public-facing rulebook. The live owner decision and evidence are tracked in
[the publication work item](https://github.com/zevarix/rust-coding-standards/issues/17).
A dated audit is evidence of what was inspected, not permanent current truth.

## Rights and attribution

Original guidelines, examples, validators and the independent crab SVG are
**MIT OR Apache-2.0**. The Forge CSS and original homepage presentation remain
**rights reserved** under their separate notice. Preserve full license texts,
copyright, source acknowledgements and skill-package notices.

Public source visibility exposes included theme source; it does not change
reuse rights. See [Licensing and reuse](licensing.md) and [Sources](sources.md).
Confirm the owner's source-exposure decision and review third-party provenance.

## Validate the exact candidate

Run the [documented source, site and Rust example checks](site-preview.md).
Verify navigation, generated anchors/search, examples, licensing and
contributor/security links at the exact proposed revision.

For skill changes, qualify discovery/installation and compare the complete
installed payload with the selected source. Preserve a consuming project's
documentation-reference choice. See [Reusable Rust skills](skills.md).

Distinguish local validation from hosted CI and inspect the actual result of
each. A successful build is not publication.

## Visibility, settings and distribution

Recheck the final source, outstanding findings and owner decision before a
private-to-public change. Public visibility requires explicit authorization
for the existing repository. Read back visibility and public access afterward.

Select branch protections and security-reporting settings deliberately; do
not assume a recommendation authorizes a settings change. Follow the
[security policy](https://github.com/zevarix/rust-coding-standards/blob/main/SECURITY.md)
without inventing a reporting address or an unconfigured feature.

Documentation hosting, a public domain, release tags and downloadable releases
remain separate choices. The included CI validates pull requests; after
owner-authorized hosting activation, successful `main` builds publish the
documentation website. See [hosting and deployment](site-preview.md#documentation-hosting).

For the initial site activation, confirm the Pages publishing source, custom
domain, domain ownership verification, HTTPS and environment branch policy.
Inspect the live homepage, rule deep links, search, assets and mobile layout.
Verify that pull requests cannot publish and that a failed validation blocks
deployment. Preserve unrelated DNS records and keep release tags separate
from documentation publication.
