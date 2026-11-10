# Preview the coding standards locally

The site uses **Zensical** and a [MkDocs-compatible configuration](https://zensical.org/docs/compatibility/mkdocs/), giving us the same Markdown source structure and familiar Material-style navigation as the [Drupal Coding Standards](https://project.pages.drupalcode.org/coding_standards/php/documentation/).

The included workflow validates pull requests and publishes successful `main` builds through GitHub Pages after hosting is activated. A local preview does **not** change repository visibility or publish a website. Review the [publication-readiness checklist](publication-readiness.md) before any distribution decision. Bind the development server to loopback on your own workstation.

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

The local build output is written into `site/`, which is deliberately ignored by Git. Do not commit generated HTML. Initial hosting activation or a change of publication destination requires the owner's approval.

## Forge visual identity (draft)

This project adds a small stylesheet (`docs/stylesheets/forge.css`) on top of
Zensical's built-in modern Material-derived theme. The original crab-inspired
SVG (`docs/assets/brand/forge-crab.svg`) acts as the logo and favicon. The SVG is **MIT OR Apache-2.0**, but the original Forge CSS and authored homepage visual theme remain all rights reserved. See [Licensing and reuse](licensing.md).
It references the broader Rustacean community but **is not Ferris artwork** or
official Rust branding. See [Sources](sources.md) for the inspiration and distinction.

The design includes a custom home hero, editorial code illustration, topic cards,
accessible focus states, dark/light palettes, responsive navigation, and reduced
motion handling. Navigation, on-page headings and full-text search remain
Zensical features; no custom JavaScript or hosted dependency was added.

The examples use **localhost:8001** to reduce conflicts with other local
development services. If that port is occupied, use any free loopback port
without stopping unrelated services.

## Why use `mkdocs.yml` instead of Zensical-only configuration?

Zensical can use an existing `mkdocs.yml`, including familiar Material navigation and Python Markdown extensions. This preserves a straightforward path to compare with Material for MkDocs or migrate later. The current design uses Zensical's `modern` theme variant; some Zensical-specific settings may need adjustment if building with classic MkDocs, so **a separate MkDocs build has not been proven** by a successful Zensical build alone.

We keep the configuration intentionally small: navigation, search, code highlighting, a light/dark choice and anchored rule headings. Add plugins, analytics or duplicated content only when they provide concrete value.

## Check documentation and Rust examples

After creating the environment and installing dependencies using the matching
setup above, run these commands from the repository root. Explicit environment
paths avoid needing to activate the virtual environment. Stop the preview server
first if it is still running in that terminal.

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe tools/verify_standards.py
.\.venv\Scripts\zensical.exe build
.\.venv\Scripts\python.exe tools/verify_standards.py --site
.\.venv\Scripts\python.exe -m unittest discover -s tools -p "test_*.py"
.\.venv\Scripts\python.exe tools/verify_rust_examples.py
```

### macOS or Linux

```sh
.venv/bin/python tools/verify_standards.py
.venv/bin/zensical build
.venv/bin/python tools/verify_standards.py --site
.venv/bin/python -m unittest discover -s tools -p "test_*.py"
.venv/bin/python tools/verify_rust_examples.py
```

The Rust example check needs installed `rustc` on `PATH` with Rust 2024 edition support. It compiles **only marked self-contained examples**, runs marked tests and fails on a broken marker; deliberate anti-examples and pseudocode are never executed. The repository uses the current compatible stable Rust toolchain for shared examples; consuming projects keep their own supported toolchain and platform policy. The GitHub Actions workflow runs the same checks with its own environment. On `main`, it uploads the generated site only after all checks pass, then deploys that artifact in the separate `github-pages` environment.

## Documentation hosting

The documentation address is **https://rcs.zevarix.com/**. Hosting uses GitHub
Pages with GitHub Actions as the publishing source; the custom domain is a
repository Pages setting. The subdomain's DNS CNAME target is
`zevarix.github.io`, without the repository name. Existing A/AAAA records at
the same subdomain conflict with that CNAME. Domain verification and HTTPS
must be checked during owner-authorized activation; preserve unrelated
website, email and verification records.

The `source-and-examples` job validates every pull request and push to `main`.
Pull requests never upload a Pages artifact or deploy. Main pushes reuse the
validated `site/` output and deploy only after that job succeeds. A manual
workflow run on `main` follows the same validation and publication path;
manual runs on another branch cannot publish. Publishing is serialized in
the `github-pages` environment, which should allow deployments only from
`main`. Only the deployment job receives Pages write and OIDC permissions.

To retry publication, use **Actions → Validate and publish Rust Coding
Standards → Run workflow → main**, or rerun the failed job after resolving
its cause. Verify the actual deployment and live website; a local or CI
build passing does not itself confirm public availability. To stop hosting,
disable the Pages site and reconcile its DNS record so it no longer points
at an unserved GitHub Pages destination.

## What to validate

1. Confirm `zensical build` exits successfully and produces `site/index.html`.
2. Open the standards index, each rule page, adoption, source links and contributor instructions.
3. Verify left navigation, built-in search and on-page headings work in the browser.
4. Check Markdown cross-links and IDs such as `RCS-PERF-001` and `RCS-SAFE-001`.
5. Treat preview as unapproved draft, not a publicly released version.

The source of the guidelines remains the Markdown files under `docs/`, not generated static HTML.
