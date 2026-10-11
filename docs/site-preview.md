# Preview the coding standards locally

The site uses **Zensical** and a [MkDocs-compatible configuration](https://zensical.org/docs/compatibility/mkdocs/), giving us the same Markdown source structure and familiar Material-style navigation as the [Drupal Coding Standards](https://project.pages.drupalcode.org/coding_standards/php/documentation/).

No hosted site, Pages workflow, public domain or deployment is configured. The GitHub repository remains **private**. Preview only on your own trusted workstation; do not expose the development web server to public networks.

## Windows PowerShell

From the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv\Scripts\zensical.exe build
.\.venv\Scripts\zensical.exe serve --dev-addr 127.0.0.1:8000
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) on **the same machine**.

## macOS or Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-docs.txt
.venv/bin/zensical build
.venv/bin/zensical serve --dev-addr 127.0.0.1:8000
```

The local build output is written into `site/`, which is deliberately ignored by Git. Do not commit generated HTML or enable a deployment job until the owner independently approves publication.

## Why use `mkdocs.yml` instead of Zensical-only configuration?

Zensical can use an existing `mkdocs.yml`, including familiar Material navigation and Python Markdown extensions. This preserves a straightforward path to compare with Material for MkDocs or migrate later. The current design uses Zensical's `modern` theme variant; some Zensical-specific settings may need adjustment if building with classic MkDocs, so **a separate MkDocs build has not been proven** by a successful Zensical build alone.

We keep the configuration intentionally small: navigation, search, code highlighting, a light/dark choice and anchored rule headings. Avoid plugins, analytics, private-site publication or content duplication unless they provide concrete value.

## What to validate

1. Confirm `zensical build` exits successfully and produces `site/index.html`.
2. Open the standards index, each rule page, adoption, source links and contributor instructions.
3. Verify left navigation, built-in search and on-page headings work in the browser.
4. Check Markdown cross-links and IDs such as `ZR-PERF-001` and `ZR-SAFE-001`.
5. Treat preview as unapproved draft, not a publicly released version.

The source of the guidelines remains the Markdown files under `docs/`, not generated static HTML.
