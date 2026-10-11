# Preview the coding standards locally

The site uses **Zensical** and a [MkDocs-compatible configuration](https://zensical.org/docs/compatibility/mkdocs/), giving us the same Markdown source structure and familiar Material-style navigation as the [Drupal Coding Standards](https://project.pages.drupalcode.org/coding_standards/php/documentation/).

No hosted site, Pages workflow, public domain or deployment is configured. The GitHub repository remains **private**. Preview only on your own trusted workstation; do not expose the development web server to public networks.

## Windows PowerShell

From the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv\Scripts\zensical.exe build
.\.venv\Scripts\zensical.exe serve --dev-addr 127.0.0.1:8001
```

Open [http://127.0.0.1:8001/](http://127.0.0.1:8001/) on **the same machine**.

## macOS or Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-docs.txt
.venv/bin/zensical build
.venv/bin/zensical serve --dev-addr 127.0.0.1:8001
```

The local build output is written into `site/`, which is deliberately ignored by Git. Do not commit generated HTML or enable a deployment job until the owner independently approves publication.

## Forge visual identity (draft)

This project adds a small stylesheet (`docs/stylesheets/forge.css`) on top of
Zensical's built-in modern Material-derived theme. The original crab-inspired
SVG (`docs/assets/brand/forge-crab.svg`) acts as the logo and favicon. The SVG is **MIT OR Apache-2.0**, but the original Forge CSS and authored homepage visual theme remain all rights reserved. See [Licensing and reuse](licensing.md).
It references the broader Rustacean community but **is not Ferris artwork** or
official Rust branding. See `docs/sources.md` for the inspiration and distinction.

The design includes a custom home hero, editorial code illustration, topic cards,
accessible focus states, dark/light palettes, responsive navigation, and reduced
motion handling. Navigation, on-page headings and full-text search remain
Zensical features; no custom JavaScript or hosted dependency was added.

The examples use **localhost:8001** to reduce conflicts with other local
development services. If that port is occupied, use any free loopback port
without stopping unrelated services.

## Why use `mkdocs.yml` instead of Zensical-only configuration?

Zensical can use an existing `mkdocs.yml`, including familiar Material navigation and Python Markdown extensions. This preserves a straightforward path to compare with Material for MkDocs or migrate later. The current design uses Zensical's `modern` theme variant; some Zensical-specific settings may need adjustment if building with classic MkDocs, so **a separate MkDocs build has not been proven** by a successful Zensical build alone.

We keep the configuration intentionally small: navigation, search, code highlighting, a light/dark choice and anchored rule headings. Avoid plugins, analytics, private-site publication or content duplication unless they provide concrete value.

## Check documentation and Rust examples

These commands run locally and in the private repository's source-validation CI:

```sh
python tools/verify_standards.py
zensical build
python tools/verify_standards.py --site
python -m unittest discover -s tools -p "test_*.py"
python tools/verify_rust_examples.py
```

The Rust example check needs installed `rustc` with Rust 2024 edition support. It compiles **only marked self-contained examples**, runs marked tests and fails on a broken marker; deliberate anti-examples and pseudocode are never executed. The repository uses the current compatible stable Rust toolchain for shared examples; consuming projects keep their own supported toolchain and platform policy. The GitHub Actions workflow validates source only and does not deploy or publish the private site.

## What to validate

1. Confirm `zensical build` exits successfully and produces `site/index.html`.
2. Open the standards index, each rule page, adoption, source links and contributor instructions.
3. Verify left navigation, built-in search and on-page headings work in the browser.
4. Check Markdown cross-links and IDs such as `RCS-PERF-001` and `RCS-SAFE-001`.
5. Treat preview as unapproved draft, not a publicly released version.

The source of the guidelines remains the Markdown files under `docs/`, not generated static HTML.
