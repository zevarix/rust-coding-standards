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

The separate v0.1.1 candidate includes owner-approved, publicly served
[privacy](https://rcs.zevarix.com/privacy/) and
[terms](https://rcs.zevarix.com/terms/) pages. The two real HTTPS pages were
independently checked for HTTP 200 and correct policy content before their
addresses were added to the manifest; no placeholder legal URLs are used.

This is **still a review candidate, not a submitted or published plugin**.
OpenAI's remote MCP review additionally needs a reviewer-accessible demo
recording, connection and domain verification using the exact portal-issued
challenge, scans of real tools and skills, and personal publisher attestations.
The current five positive / three negative review prompts are candidate test
cases; verify them against the real client before submission.

The new package is meant to be uploaded as **With MCP / a new plugin**.
It cannot be attached to the older skills-only draft. Domain verification,
scanning, individual developer verification, legal attestations, submission
and eventual publication are separate owner-controlled steps. Do not describe
the ZIP or a successful build as an approved/public ChatGPT plugin.

See [RCS issue #64](https://github.com/zevarix/rust-coding-standards/issues/64).

