# RCS connected plugin — technical candidate

This is a **separate** RCS plugin candidate, not an update to the existing
private skills-only `rust-coding-standards` v0.1.1 installation.

It packages the original open-licensed Forge icon and canonical `rcs-guidance`
and `rust-performance` skill trees without maintaining duplicate skill files.
Its single remote Streamable HTTP MCP server is
`https://rcsmcp.zevarix.com/mcp`, offering the genuine, read-only
`search_rules`, `get_rule`, `get_guidance`, and `catalog_info` tools.
Those tools cannot access private user repositories or execute code.

Build and test with:

```sh
python tools/package_rcs_mcp_plugin.py
python -m unittest discover -s tools -p "test_*.py"
```

The package source and ZIP are **not yet submission ready**. OpenAI's remote
MCP review requires the individual publisher to supply **approved, already
published** HTTPS privacy and terms URLs and a reviewer-accessible demo
recording. Their absence is intentional; never substitute `example.com` or
an invented policy. Verify actual hosting-side request metadata retention,
logs and applicable user controls before drafting legal representations.
The current five positive / three negative review prompts are candidate
test cases; verify them against the live endpoint before submission.

The new package is meant to be uploaded as **With MCP / a new plugin**.
It cannot be attached to the older skills-only draft. Domain verification,
scanning, individual developer verification, legal attestations, submission
and eventual publication are separate owner-controlled steps. Do not describe
the ZIP or a successful build as an approved/public ChatGPT plugin.

See [RCS issue #64](https://github.com/zevarix/rust-coding-standards/issues/64).

